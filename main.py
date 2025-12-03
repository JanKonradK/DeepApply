#!/usr/bin/env python3
"""
Nyx Venatrix - Autonomous Job Application Agent
Main Entry Point
"""
import os
import sys
import argparse
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NyxVenatrix")

def run_agent(args):
    """Run the main agent service"""
    logger.info("Starting Agent Service...")
    os.chdir("services/agent")
    subprocess.run(["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

def run_simulation(args):
    """Run the multi-agent simulation"""
    logger.info("Starting Simulation...")
    subprocess.run([sys.executable, "tests/simulation_run.py"])

def run_demo(args):
    """Run the production demo"""
    logger.info("Starting Production Demo...")
    subprocess.run([sys.executable, "tests/production_demo.py"])

def run_dashboard(args):
    """Run the Streamlit dashboard"""
    logger.info("Starting Dashboard...")
    subprocess.run(["streamlit", "run", "services/dashboard/src/main.py"])

def main():
    parser = argparse.ArgumentParser(description="Nyx Venatrix CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Agent
    agent_parser = subparsers.add_parser("agent", help="Run the agent service")

    # Simulation
    sim_parser = subparsers.add_parser("simulate", help="Run multi-agent simulation")

    # Demo
    demo_parser = subparsers.add_parser("demo", help="Run production demo")

    # Dashboard
    dash_parser = subparsers.add_parser("dashboard", help="Run analytics dashboard")

    args = parser.parse_args()

    if args.command == "agent":
        run_agent(args)
    elif args.command == "simulate":
        run_simulation(args)
    elif args.command == "demo":
        run_demo(args)
    elif args.command == "dashboard":
        run_dashboard(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
