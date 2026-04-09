import pandas as pd
from unittest.mock import MagicMock, patch

from app.portfolio import Portfolio

@patch('chromadb.PersistentClient')
@patch('pandas.read_csv')
def test_portfolio_initialization(mock_read_csv, mock_chroma):
    # Setup mock data
    mock_df = pd.DataFrame({
        'Techstack': ['React', 'Python'],
        'Links': ['link1', 'link2']
    })
    mock_read_csv.return_value = mock_df
    
    # Initialize Portfolio
    with patch('os.path.exists', return_value=True):
        portfolio = Portfolio(file_name="dummy.csv")
    
    assert portfolio.file_path.endswith('dummy.csv')
    mock_read_csv.assert_called_once()
    mock_chroma.assert_called_once()

if __name__ == "__main__":
    print("Test template created for Portfolio. Full integration tests require a live ChromaDB environment.")
