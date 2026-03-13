import subprocess
import os
import pandas as pd

def test_cli_execution():
    """Test the CLI command 'autofcholv' via subprocess."""
    # Create a temporary input file
    input_file = "test_input.csv"
    output_file = "output_features.csv"
    
    df = pd.DataFrame({'close': [1, 2, 3, 4, 5, 6], 'volume': [10, 20, 30, 40, 50, 60]})
    df.to_csv(input_file, index=False)
    
    try:
        # Get path to the CLI executable in venv
        cli_executable = os.path.join(os.getcwd(), "venv", "bin", "autofcholv")
        
        # Run CLI 
        result = subprocess.run([cli_executable, input_file], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert os.path.exists(output_file)
        
        # Verify output content
        out_df = pd.read_csv(output_file)
        assert 'close_pct_change' in out_df.columns
        
    finally:
        # Cleanup
        if os.path.exists(input_file): os.remove(input_file)
        if os.path.exists(output_file): os.remove(output_file)
