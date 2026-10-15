"""CLI entrypoint for NBA betting prediction system."""

import argparse
import sys
from src.utils.logger import logger
from src.utils.db import init_db

def main():
    parser = argparse.ArgumentParser(description="NBA Betting Prediction System (Spain: bet365 / Winamax)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: init-db
    subparsers.add_parser("init-db", help="Initialize SQLite tables")

    # Command: ingest
    ingest_p = subparsers.add_parser("ingest", help="Ingest NBA data from stats.nba.com")
    ingest_p.add_argument("--seasons", type=str, default="2023-24,2024-25", help="Comma-separated seasons")

    # Command: features
    feat_p = subparsers.add_parser("features", help="Compute feature matrix")
    feat_p.add_argument("--seasons", type=str, default=None, help="Comma-separated seasons")

    # Command: train
    train_p = subparsers.add_parser("train", help="Train LightGBM + XGBoost models")
    train_p.add_argument("--features", type=str, default="data/processed/features.parquet")

    # Command: report
    subparsers.add_parser("report", help="Generate daily betting report")

    # Command: dashboard
    dash_p = subparsers.add_parser("dashboard", help="Start FastAPI Web Dashboard")
    dash_p.add_argument("--port", type=int, default=8050, help="Web server port (default 8050)")
    dash_p.add_argument("--host", type=str, default="127.0.0.1", help="Host address")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "init-db":
        init_db()

    elif args.command == "ingest":
        from src.ingestion.nba_stats import ingest_historical_seasons
        init_db()
        seasons = [s.strip() for s in args.seasons.split(",")]
        ingest_historical_seasons(seasons)

    elif args.command == "features":
        from src.features.builder import build_feature_matrix
        seasons = [s.strip() for s in args.seasons.split(",")] if args.seasons else None
        build_feature_matrix(seasons)

    elif args.command == "train":
        from src.models.train import train_all_models
        train_all_models(feature_matrix_path=args.features)

    elif args.command == "report":
        from src.dashboard.app import get_enriched_players
        from src.betting.report import generate_recommendations, print_console_report
        players = get_enriched_players()
        recs = generate_recommendations(players)
        print_console_report(recs)

    elif args.command == "dashboard":
        import uvicorn
        logger.info(f"Starting NBAEdge Dashboard on http://{args.host}:{args.port}")
        uvicorn.run("src.dashboard.app:app", host=args.host, port=args.port, reload=False)

if __name__ == "__main__":
    main()

