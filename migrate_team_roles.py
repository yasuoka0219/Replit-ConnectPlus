#!/usr/bin/env python3
"""
Database migration helper: add teams table, role columns, and link existing data.
"""
from app import app, db
from models import User, Deal, Team


def run_migration():
    with app.app_context():
        print("=" * 70)
        print("CONNECT+ Team & Role Migration")
        print("=" * 70)

        # Ensure tables/columns exist
        print("Creating/Updating tables via SQLAlchemy...")
        db.create_all()
        print("✓ Base schema ensured")

        default_team = Team.query.order_by(Team.id.asc()).first()
        if not default_team:
            default_team = Team(name="メインチーム", description="自動作成された標準チーム")
            db.session.add(default_team)
            db.session.commit()
            print("✓ Default team created")

        # Assign roles (first user becomes admin if no admins yet)
        users = User.query.order_by(User.id.asc()).all()
        if not users:
            print("No users found. Nothing else to migrate.")
            return

        has_admin = any(user.role == 'admin' for user in users if user.role)
        for idx, user in enumerate(users):
            if not user.role:
                if not has_admin and idx == 0:
                    user.role = 'admin'
                    has_admin = True
                else:
                    user.role = 'member'
            if not user.team_id:
                user.team_id = default_team.id
        db.session.commit()
        print("✓ Users updated with roles and team assignments")

        # Assign deals to teams
        deals = Deal.query.all()
        for deal in deals:
            if not deal.team_id:
                if deal.assignee_user and deal.assignee_user.team_id:
                    deal.team_id = deal.assignee_user.team_id
                else:
                    deal.team_id = default_team.id
        db.session.commit()
        print("✓ Deals linked to teams")

        print("=" * 70)
        print("Migration completed successfully.")


if __name__ == '__main__':
    run_migration()





