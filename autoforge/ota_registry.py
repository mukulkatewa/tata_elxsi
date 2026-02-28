"""
OTA Service Registry for AutoForge.

Manages dynamically registered services that can be added at runtime.
Supports simulation of Over-The-Air (OTA) updates and subscription-based
feature activation for SDV platforms.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class ServiceEntry:
    """A registered service in the OTA registry."""
    service_id: str
    name: str
    version: str
    description: str
    language: str  # cpp, rust, kotlin
    status: str  # "active", "inactive", "pending_update"
    code_path: Optional[str] = None
    test_path: Optional[str] = None
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    subscription_tier: str = "base"  # base, premium, enterprise
    signals_used: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class OTAServiceRegistry:
    """
    Service registry for managing OTA-deployable services.
    
    Features:
    - Register new services dynamically
    - Simulate OTA updates (version bump)
    - Subscription-based feature tiers
    - Persistent storage via JSON
    """
    
    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize the OTA service registry.
        
        Args:
            registry_path: Path to store the registry JSON file.
                          Defaults to autoforge/data/service_registry.json
        """
        if registry_path is None:
            registry_path = Path("autoforge/data/service_registry.json")
        
        self.registry_path = registry_path
        self.services: Dict[str, ServiceEntry] = {}
        
        # Load existing registry if it exists
        self._load()
    
    def register_service(self, name: str, description: str, language: str = "cpp",
                         code_path: str = None, test_path: str = None,
                         signals_used: List[str] = None, 
                         subscription_tier: str = "base",
                         metadata: Dict[str, Any] = None) -> ServiceEntry:
        """
        Register a new service in the registry.
        
        Args:
            name: Human-readable service name
            description: Service description
            language: Programming language (cpp, rust, kotlin)
            code_path: Path to generated source code
            test_path: Path to test file
            signals_used: List of VSS signals used
            subscription_tier: Required subscription tier
            metadata: Additional metadata
            
        Returns:
            The registered ServiceEntry
        """
        # Generate service ID
        service_id = name.lower().replace(' ', '_').replace('-', '_')
        
        # Check for existing service (update version)
        version = "1.0.0"
        if service_id in self.services:
            existing = self.services[service_id]
            version = self._increment_version(existing.version)
            print(f"   📦 Updating existing service: {service_id} v{existing.version} → v{version}")
        else:
            print(f"   📦 Registering new service: {service_id} v{version}")
        
        entry = ServiceEntry(
            service_id=service_id,
            name=name,
            version=version,
            description=description,
            language=language,
            status="active",
            code_path=code_path,
            test_path=test_path,
            signals_used=signals_used or [],
            subscription_tier=subscription_tier,
            metadata=metadata or {}
        )
        
        self.services[service_id] = entry
        self._save()
        
        return entry
    
    def simulate_ota_update(self, service_id: str, new_code: str = None,
                            new_version: str = None) -> Optional[ServiceEntry]:
        """
        Simulate an OTA update for a registered service.
        
        Args:
            service_id: ID of the service to update
            new_code: Updated source code (optional)
            new_version: New version string (optional, auto-incremented)
            
        Returns:
            Updated ServiceEntry or None if not found
        """
        if service_id not in self.services:
            print(f"⚠️  Service '{service_id}' not found in registry")
            return None
        
        entry = self.services[service_id]
        entry.version = new_version or self._increment_version(entry.version)
        entry.updated_at = datetime.now().isoformat()
        entry.status = "active"
        
        # If new code provided, save it
        if new_code and entry.code_path:
            try:
                Path(entry.code_path).write_text(new_code, encoding='utf-8')
            except Exception:
                pass  # Non-critical
        
        self._save()
        print(f"   📡 OTA Update: {entry.name} → v{entry.version}")
        
        return entry
    
    def get_active_services(self, subscription_tier: str = None) -> List[ServiceEntry]:
        """
        Get all active services, optionally filtered by subscription tier.
        
        Args:
            subscription_tier: Filter by tier (base, premium, enterprise)
            
        Returns:
            List of active ServiceEntry objects
        """
        services = [s for s in self.services.values() if s.status == "active"]
        
        if subscription_tier:
            tier_hierarchy = {"base": 0, "premium": 1, "enterprise": 2}
            tier_level = tier_hierarchy.get(subscription_tier, 0)
            services = [s for s in services 
                       if tier_hierarchy.get(s.subscription_tier, 0) <= tier_level]
        
        return services
    
    def deactivate_service(self, service_id: str) -> bool:
        """Deactivate a service (simulate unsubscribe)."""
        if service_id in self.services:
            self.services[service_id].status = "inactive"
            self._save()
            return True
        return False
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get a summary of the service registry."""
        active = [s for s in self.services.values() if s.status == "active"]
        inactive = [s for s in self.services.values() if s.status == "inactive"]
        
        return {
            "total_services": len(self.services),
            "active": len(active),
            "inactive": len(inactive),
            "by_language": self._count_by_field("language"),
            "by_tier": self._count_by_field("subscription_tier"),
            "services": [
                {
                    "id": s.service_id,
                    "name": s.name,
                    "version": s.version,
                    "status": s.status,
                    "language": s.language,
                    "tier": s.subscription_tier
                }
                for s in self.services.values()
            ]
        }
    
    def _count_by_field(self, field_name: str) -> Dict[str, int]:
        """Count services grouped by a field value."""
        counts = {}
        for service in self.services.values():
            value = getattr(service, field_name, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    def _increment_version(self, version: str) -> str:
        """Increment the patch version number."""
        parts = version.split('.')
        try:
            parts[-1] = str(int(parts[-1]) + 1)
        except ValueError:
            parts.append("1")
        return '.'.join(parts)
    
    def _save(self) -> None:
        """Save registry to JSON file."""
        try:
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            data = {sid: asdict(entry) for sid, entry in self.services.items()}
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save registry: {e}")
    
    def _load(self) -> None:
        """Load registry from JSON file."""
        if not self.registry_path.exists():
            return
        
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for sid, entry_data in data.items():
                self.services[sid] = ServiceEntry(**entry_data)
                
        except Exception as e:
            print(f"Warning: Could not load registry: {e}")
