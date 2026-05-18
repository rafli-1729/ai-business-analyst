import glob
import re

for filepath in glob.glob('core_analytics/agents/*_agent.py'):
    with open(filepath, 'r') as f:
        content = f.read()

    # Import
    if 'parse_agent_response' not in content:
        content = content.replace('from core_analytics.agents.base import AgentState, AgentArtifact, BaseAgent', 'from core_analytics.agents.base import AgentState, AgentArtifact, BaseAgent, parse_agent_response')

    # General pattern
    pattern = r'artifact = AgentArtifact\([\s\S]*?content=response\["messages"\]\[-1\]\.content\n    \)\n    \n    return \{"artifacts": \[artifact\], "active_agents": \["([^"]+)"\]\}'
    
    def repl(m):
        agent_name = m.group(1)
        return f'artifacts = parse_agent_response(response["messages"][-1].content, "{agent_name}")\n    return {{"artifacts": artifacts, "active_agents": ["{agent_name}"]}}'
    
    content = re.sub(pattern, repl, content)

    # Sales agent specific pattern
    pattern2 = r'# Sales creates an executive summary artifact\n    artifact = AgentArtifact\([\s\S]*?content=response\["messages"\]\[-1\]\.content\n    \)\n    \n    return \{"artifacts": \[artifact\], "active_agents": \["([^"]+)"\]\}'
    content = re.sub(pattern2, repl, content)

    with open(filepath, 'w') as f:
        f.write(content)
print('Done patching agents')
