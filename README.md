# Desktop Pet

A cute desktop pet that shows system information and can chat with you using DeepSeek AI.

## Features

- Cute desktop pet with multiple animations
- System information display (CPU, Memory, Network)
- Chat with AI using DeepSeek
- Multiple theme colors
- Customizable settings

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/desktop-pet.git
   cd desktop-pet
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your DeepSeek API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your DeepSeek API key
   ```

## Usage

Run the program:
```bash
python main.py
```

## Configuration

You can customize the following settings in the `.env` file:

- `DEEPSEEK_API_KEY`: Your DeepSeek API key
- `ANIMATION_FPS`: Animation frame rate (default: 30)
- `WINDOW_WIDTH`: Pet window width (default: 300)
- `WINDOW_HEIGHT`: Pet window height (default: 300)
- `CURRENT_THEME`: Theme color (default: "粉色主题")

## Development

The project structure:
```
desktop-pet/
├── src/
│   ├── config.py      # Configuration management
│   ├── deepseek_client.py  # DeepSeek API client
│   ├── pet_window.py  # Main window and UI
│   ├── system_monitor.py  # System monitoring
│   └── system_tray.py  # System tray integration
├── main.py           # Entry point
├── requirements.txt  # Dependencies
├── .env.example     # Example configuration
└── README.md        # Documentation
```

## License

MIT License 