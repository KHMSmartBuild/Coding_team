# Dataset requirements for each agent

agent_requirements = {
    'A1 - Project Manager': ['Project management data', 'communication data', 'decision-making data'],
    'A2 - Software Architect': ['Software architecture data', 'requirements data', 'testing data'],
    'A3 - Frontend Developer': ['User interface data', 'code data', 'testing data'],
    'A4 - Backend Developer': ['Database data', 'code data', 'testing data'],
    'A5 - Data Engineer': ['Data collection data', 'data cleaning data', 'data analysis data'],
    'A6 - Data Scientist': ['Data analysis data', 'business intelligence data', 'visualization data'],
    'A7 - Machine Learning Engineer': ['Data analysis data', 'machine learning data', 'model training data'],
    'A8 - DevOps Engineer': ['Deployment data', 'monitoring data', 'security data'],
    'A9 - Quality Assurance Engineer': ['Test plans', 'test cases', 'test results', 'bug reports', 'bug fixes', 'quality assurance metrics'],
    'A10 - Security Engineer': ['Security assessments', 'security recommendations', 'security monitoring and incident response']
}

# Print table of agent requirements
print('| Agent | Dataset Requirements |')
print('|-------|----------------------|')
for agent, requirements in agent_requirements.items():
    requirements = ", ".join(requirements)
    print(f"| {agent} | {requirements} |")
