# Fast Soroban Solver

A real-time math problem solver for the Soroban app on Android devices. Uses OCR to extract equations from screen captures, solves them automatically, and maintains a history of solved problems.

## Features

- **Real-time Solving**: Continuously monitors and solves math problems from connected Android device
- **OCR Integration**: Adjustable threshold for accurate text recognition
- **Division Mode**: Toggle support for division operations
- **History Management**: Saves and loads solved problems to CSV
- **Keyboard Shortcuts**: 
  - Space: Toggle solving on/off
  - Ctrl+D: Toggle division mode
  - Ctrl+L: Reset application
- **Live UI**: Displays captured images, recognized text, and solutions
- **Error Handling**: Robust processing with logging and retry mechanisms

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Alexis12119/Soroban-Solver.git
   cd soroban-solver
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure Android device is connected with USB debugging enabled.

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Adjust OCR threshold and minimum numbers if needed
3. Click "Start Solving" or press Space to begin real-time solving
4. Toggle division mode with Ctrl+D if solving division problems
5. View solved problems in the history and logs

## Requirements

- Python 3.x
- Android device with Soroban app installed
- USB debugging enabled on device
- Dependencies listed in `requirements.txt`

## Troubleshooting

- Ensure Android device is properly connected and recognized
- Adjust OCR threshold for better text recognition
- Check logs for error messages and processing status

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
