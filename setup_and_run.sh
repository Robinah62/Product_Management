#!/bin/bash
# ─────────────────────────────────────────────────
#  Kibuuka's Corner Shop – Quick Setup Script
#  Run this once to set up and start the app
# ─────────────────────────────────────────────────

echo ""
echo "🛒  Kibuuka's Corner Shop – Setup"
echo "=================================="

# 1. Create virtual environment
echo "📦  Creating virtual environment..."
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Install Django
echo "⚙️   Installing Django..."
pip install -r requirements.txt

# 4. Run migrations
echo "🗄️   Setting up database..."
python manage.py migrate

# 5. Create superuser (owner/admin account)
echo ""
echo "👤  Create your admin/owner account:"
python manage.py createsuperuser

# 6. Start server
echo ""
echo "🚀  Starting server at http://127.0.0.1:8000"
echo "    Press Ctrl+C to stop."
echo ""
python manage.py runserver
