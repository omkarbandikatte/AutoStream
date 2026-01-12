from app.database import save_user

def mock_lead_capture(name: str, email: str, platform: str, plan: str = None):
    """Capture lead information and store in database"""
    try:
        # Store in database
        save_user(name, email, platform, plan)
        print(f"✓ Lead captured successfully: {name}, {email}, {platform}, Plan: {plan}")
        return True
    except Exception as e:
        print(f"✗ Error capturing lead: {str(e)}")
        return False