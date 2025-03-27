#!/usr/bin/env python
"""
PCR Optimizer başlatma scripti.
"""

from src.app import app

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000) 