# past-price-similarity
past price similarity analysis


Here is a README file for the `past-price-similarity.py` script:

```markdown
# Past Price Similarity Analysis

This repository contains a script to analyze past price similarity using historical data from Binance. The script downloads historical kline data, normalizes the price series, calculates Euclidean distances, and visualizes the results.

## Features

- **Download Historical Data**: Fetches historical kline data from Binance and saves it to a CSV file.
- **Normalization**: Normalizes price series relative to the first bar.
- **Euclidean Distance Calculation**: Computes the Euclidean distance between normalized price series.
- **Similarity Analysis**: Identifies the most similar past price blocks and visualizes the future price movement.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kobzeci/past-price-similarity.git
   cd past-price-similarity
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Binance API credentials in a file named `config_f.py`:
   ```python
   api_key = 'your_binance_api_key'
   api_secret = 'your_binance_api_secret'
   ```

## Usage

To run the script, execute the following command and provide the required inputs:

```bash
python past-price-similarity.py
```

You will be prompted to enter the following details:
- Instrument (e.g., BTCUSDT)
- Period (e.g., 1m, 5m, 15m, 1h, 4h, 1d)
- Start date (YYYY-MM-DD)
- Number of bars to analyze

You can choose to use an existing CSV file or download new data from Binance.

## Example

Here is how you can run the script:

```bash
python past-price-similarity.py
```

Follow the prompts to enter the instrument, period, start date, and number of bars to analyze. The script will download the data (if necessary), perform the similarity analysis, and display the results.

## Output

The script will display a plot showing the normalized price series and the most similar past price blocks. It will also print a table with the similarity analysis results, including the start and end times of the similar periods, the Euclidean distance, and the percentage change in future prices.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Contact

For any questions or inquiries, please contact [your-email@example.com](mailto:your-email@example.com).

```

Feel free to customize the README with your own contact information and any additional details you find relevant.
