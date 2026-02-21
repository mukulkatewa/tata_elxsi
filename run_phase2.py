#!/usr/bin/env python3
"""
AutoForge Phase 2 Entry Point

This script provides the main entry point for the AutoForge multi-agent
code generation system. It supports both demo mode (with preset requirements)
and interactive mode (continuous user input).

Usage:
    python run_phase2.py           # Interactive mode
    python run_phase2.py --demo    # Demo mode with preset requirements
"""

import sys
import argparse
from autoforge.orchestrator import AutoForgeOrchestrator


def main():
    """Main entry point for AutoForge Phase 2."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='AutoForge Phase 2: Multi-Agent Code Generation System'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run demo mode with preset requirements'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize orchestrator
        orchestrator = AutoForgeOrchestrator()
        
        if args.demo:
            # Demo mode: Execute preset requirements
            print("\n" + "="*70)
            print("🎬 AutoForge Demo Mode")
            print("="*70)
            print("\nExecuting preset requirements to demonstrate system capabilities...\n")
            
            # Preset requirement 1: Tyre pressure monitoring
            requirement1 = (
                "Create a tyre pressure monitoring service that alerts when "
                "pressure drops below 28 PSI on any wheel"
            )
            print(f"\n{'='*70}")
            print(f"Demo 1/2: Tyre Pressure Monitoring")
            print(f"{'='*70}")
            orchestrator.run(requirement1)
            
            # Preset requirement 2: Battery state of charge
            requirement2 = (
                "Create a battery state of charge service that monitors EV range "
                "and triggers low battery warnings below 20%"
            )
            print(f"\n{'='*70}")
            print(f"Demo 2/2: Battery State of Charge")
            print(f"{'='*70}")
            orchestrator.run(requirement2)
            
            print("\n" + "="*70)
            print("✅ Demo Complete!")
            print("="*70)
            print("\nCheck the 'autoforge/outputs/' directory for generated code.")
            
        else:
            # Interactive mode
            orchestrator.run_interactive()
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Exiting AutoForge.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        print("\nPlease check your configuration and try again.")
        sys.exit(1)


if __name__ == '__main__':
    main()
