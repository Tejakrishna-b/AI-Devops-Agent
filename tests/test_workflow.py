import subprocess

def test_agent_workflow():
    result = subprocess.run(['python', 'src/main.py'], capture_output=True, text=True)
    assert "Workflow complete." in result.stdout
    print("Test passed: Workflow executed successfully.")

if __name__ == "__main__":
    test_agent_workflow()
