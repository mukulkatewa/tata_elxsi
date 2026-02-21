#!/usr/bin/env python3
"""
Script to fix all dashboard errors by replacing deprecated Streamlit parameters.
"""

import re
from pathlib import Path


def fix_charts_py():
    """Fix autoforge/dashboard/components/charts.py line 161."""
    file_path = Path("autoforge/dashboard/components/charts.py")
    content = file_path.read_text()
    
    # Replace **CHART_THEME with **battery_theme
    content = content.replace("**CHART_THEME", "**battery_theme")
    
    file_path.write_text(content)
    print(f"✓ Fixed {file_path}")


def fix_gauges_py():
    """Fix autoforge/dashboard/components/gauges.py - replace use_container_width with width='stretch'."""
    file_path = Path("autoforge/dashboard/components/gauges.py")
    content = file_path.read_text()
    
    # Replace all occurrences of use_container_width=True with width='stretch'
    content = content.replace(
        "st.plotly_chart(fig, use_container_width=True)",
        "st.plotly_chart(fig, width='stretch')"
    )
    
    file_path.write_text(content)
    print(f"✓ Fixed {file_path}")


def fix_alerts_py():
    """Fix autoforge/dashboard/components/alerts.py - replace use_container_width with width='stretch'."""
    file_path = Path("autoforge/dashboard/components/alerts.py")
    content = file_path.read_text()
    
    # Replace use_container_width=True with width='stretch' in st.dataframe
    content = content.replace(
        "st.dataframe(df, use_container_width=True, hide_index=True)",
        "st.dataframe(df, width='stretch', hide_index=True)"
    )
    
    file_path.write_text(content)
    print(f"✓ Fixed {file_path}")


def fix_app_py():
    """Fix autoforge/dashboard/app.py - replace use_container_width with width='stretch'."""
    file_path = Path("autoforge/dashboard/app.py")
    content = file_path.read_text()
    
    # Replace use_container_width=True with width='stretch' in buttons
    content = content.replace(
        'st.button("Apply", use_container_width=True)',
        'st.button("Apply", width=\'stretch\')'
    )
    content = content.replace(
        'st.button("Reset", use_container_width=True)',
        'st.button("Reset", width=\'stretch\')'
    )
    
    # Replace use_container_width=True with width='stretch' in dataframe
    content = content.replace(
        "st.dataframe(display_df, use_container_width=True, hide_index=True)",
        "st.dataframe(display_df, width='stretch', hide_index=True)"
    )
    
    file_path.write_text(content)
    print(f"✓ Fixed {file_path}")


def main():
    """Run all fixes."""
    print("Starting dashboard error fixes...\n")
    
    try:
        fix_charts_py()
        fix_gauges_py()
        fix_alerts_py()
        fix_app_py()
        
        print("\n✅ All dashboard errors fixed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
