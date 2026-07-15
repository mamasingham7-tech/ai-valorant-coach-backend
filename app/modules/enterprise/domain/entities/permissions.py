from typing import Dict, Set

# Maps Roles to permissions strings
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "guest": set(),
    "user": {"read_profile", "update_profile", "upload_matches"},
    "premium": {"read_profile", "update_profile", "upload_matches", "manage_experiments"},
    "coach": {"read_profile", "update_profile", "upload_matches"},
    "admin": {
        "read_profile", "update_profile", "upload_matches", "manage_users",
        "read_audit_logs", "manage_models", "register_plugins", "rollout_models",
        "manage_feature_flags", "manage_experiments", "read_system_stats"
    },
    "system": {
        "read_profile", "update_profile", "upload_matches", "manage_users",
        "read_audit_logs", "manage_models", "register_plugins", "rollout_models",
        "manage_feature_flags", "manage_experiments", "read_system_stats"
    }
}
