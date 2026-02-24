from typing import List, Dict
import json
import logging

def load_jsonl(file_path: str) -> List[Dict]:
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def setup_logging(log_file: str) -> None:
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def log_metrics(metrics: Dict) -> None:
    for key, value in metrics.items():
        logging.info(f"{key}: {value}")

def save_model_checkpoint(model, output_dir: str) -> None:
    model.save_pretrained(output_dir)