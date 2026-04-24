def build_system_prompt(org_name: str, user_role: str) -> str:
    return f"""
You are an AI assistant for {org_name}.
You help organization admins and members with insights about their organization.
The current user has the role: {user_role}.
Always be professional, concise, and helpful.
Only answer based on the data provided to you.
Never make up information that is not in the context.
"""

def build_user_prompt(query: str, context: dict) -> str:
    return f"""
Here is the current organization data:
Organization: {context.get('org_name')}
Total Users: {context.get('total_users')}
Subscription Plan: {context.get('plan')}
Subscription Status: {context.get('status')}
Users in the organization:
{context.get('users_list')}
Pending Invitations: {context.get('pending_invites')}
Active API Keys: {context.get('active_keys')}
User Question: {query}
Please answer based only on the data above.
"""