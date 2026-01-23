#!/usr/bin/env python
"""
Database seeding script - run from backend directory: python manage.py seed_all
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.extensions import db
from backend.models import ComplaintEmailConfig, Department

app = create_app()

DEPARTMENTS = [
    {"name": "Smart Card Services", "official_email": "smartcard@kdtransco.in"},
    {"name": "Smart City Card", "official_email": "smartcity@kdtransco.in"},
    {"name": "Smart Pass Services", "official_email": "smartpass@kdtransco.in"},
    {"name": "Ticket Services", "official_email": "tickets@kdtransco.in"},
    {"name": "Operations", "official_email": "operations@kdtransco.in"},
    {"name": "Human Resources", "official_email": "hr@kdtransco.in"},
    {"name": "Support", "official_email": "support@kdtransco.in"},
    {"name": "Finance", "official_email": "finance@kdtransco.in"},
    {"name": "Administration", "official_email": "admin@kdtransco.in"},
]

EMAIL_CONFIGS = [
    # KTCL Smart Card complaints
    {"problem_type": "ktcl_smart_card", "sub_problem_type": "website_recharge", "to_email": "smartcard@kdtransco.in", "cc_email": "support@kdtransco.in"},
    {"problem_type": "ktcl_smart_card", "sub_problem_type": "mobile_app_recharge", "to_email": "smartcard@kdtransco.in", "cc_email": "support@kdtransco.in"},
    {"problem_type": "ktcl_smart_card", "sub_problem_type": "damaged_card", "to_email": "smartcard@kdtransco.in", "cc_email": "support@kdtransco.in"},
    {"problem_type": "ktcl_smart_card", "sub_problem_type": "lost_card", "to_email": "smartcard@kdtransco.in", "cc_email": "support@kdtransco.in"},
    {"problem_type": "ktcl_smart_card", "sub_problem_type": "refund", "to_email": "finance@kdtransco.in", "cc_email": "smartcard@kdtransco.in"},
    
    # Smart City Card complaints
    {"problem_type": "smartcity_card", "sub_problem_type": "smartcity_card_recharge", "to_email": "smartcity@kdtransco.in", "cc_email": "support@kdtransco.in"},
    
    # Smart Pass complaints
    {"problem_type": "smart_pass", "sub_problem_type": "smart_pass_application", "to_email": "smartpass@kdtransco.in", "cc_email": "support@kdtransco.in"},
    {"problem_type": "smart_pass", "sub_problem_type": "smart_pass_renewal_website", "to_email": "smartpass@kdtransco.in", "cc_email": "support@kdtransco.in"},
    {"problem_type": "smart_pass", "sub_problem_type": "smart_pass_renewal_mobile_app", "to_email": "smartpass@kdtransco.in", "cc_email": "support@kdtransco.in"},
    {"problem_type": "smart_pass", "sub_problem_type": "smart_pass_wallet_recharge", "to_email": "smartpass@kdtransco.in", "cc_email": "support@kdtransco.in"},
    {"problem_type": "smart_pass", "sub_problem_type": "damaged_pass", "to_email": "smartpass@kdtransco.in", "cc_email": "support@kdtransco.in"},
    {"problem_type": "smart_pass", "sub_problem_type": "lost_pass", "to_email": "smartpass@kdtransco.in", "cc_email": "support@kdtransco.in"},
    
    # Tickets complaints
    {"problem_type": "tickets", "sub_problem_type": "mobile_ticket_issue", "to_email": "tickets@kdtransco.in", "cc_email": "support@kdtransco.in"},
    {"problem_type": "tickets", "sub_problem_type": "upi_ticket_issue", "to_email": "tickets@kdtransco.in", "cc_email": "support@kdtransco.in"},
    
    # Bus Service complaints
    {"problem_type": "bus_service", "sub_problem_type": "service_complaint", "to_email": "operations@kdtransco.in", "cc_email": "support@kdtransco.in"},
    {"problem_type": "bus_service", "sub_problem_type": "driver_behaviour", "to_email": "hr@kdtransco.in", "cc_email": "operations@kdtransco.in"},
    {"problem_type": "bus_service", "sub_problem_type": "conductor_behaviour", "to_email": "hr@kdtransco.in", "cc_email": "operations@kdtransco.in"},
    
    # Staff complaints
    {"problem_type": "staff", "sub_problem_type": "staff_behaviour", "to_email": "hr@kdtransco.in", "cc_email": "admin@kdtransco.in"},
    {"problem_type": "staff", "sub_problem_type": "service_delay", "to_email": "operations@kdtransco.in", "cc_email": "admin@kdtransco.in"},
    
    # General/Others
    {"problem_type": "others", "sub_problem_type": "general_complaint", "to_email": "support@kdtransco.in", "cc_email": "admin@kdtransco.in"},
]


def seed_departments():
    """Add departments to database"""
    with app.app_context():
        print("\n📋 Seeding Departments...")
        count = 0
        for dept_data in DEPARTMENTS:
            existing = Department.query.filter_by(name=dept_data["name"]).first()
            if existing:
                print(f"  ✓ {dept_data['name']} (already exists)")
                continue
            
            dept = Department(
                name=dept_data["name"],
                official_email=dept_data["official_email"],
                is_active=True
            )
            db.session.add(dept)
            count += 1
            print(f"  ✓ Added: {dept_data['name']}")
        
        db.session.commit()
        print(f"✅ Added {count} new departments\n")


def seed_email_configs():
    """Add email configurations to database"""
    with app.app_context():
        print("📧 Seeding Email Configurations...")
        count = 0
        for config_data in EMAIL_CONFIGS:
            existing = ComplaintEmailConfig.query.filter_by(
                problem_type=config_data["problem_type"],
                sub_problem_type=config_data["sub_problem_type"]
            ).first()
            
            if existing:
                print(f"  ✓ {config_data['problem_type']}/{config_data['sub_problem_type']} (already exists)")
                continue
            
            config = ComplaintEmailConfig(
                problem_type=config_data["problem_type"],
                sub_problem_type=config_data["sub_problem_type"],
                to_email=config_data["to_email"],
                cc_email=config_data.get("cc_email"),
                is_active=True
            )
            db.session.add(config)
            count += 1
            print(f"  ✓ Added: {config_data['problem_type']}/{config_data['sub_problem_type']}")
        
        db.session.commit()
        print(f"✅ Added {count} new email configurations\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "seed_all":
        try:
            seed_departments()
            seed_email_configs()
            print("🎉 Database populated successfully!")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("Usage: python manage.py seed_all")
