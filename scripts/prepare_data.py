import argparse
from openrag_cfpb.prepare import prepare

parser = argparse.ArgumentParser(description="Prepare CFPB historical narrative export")
parser.add_argument("--input", required=True, help="Path to CFPB CSV or .csv.zip export")
parser.add_argument("--output", default="data/processed")
parser.add_argument("--sample-size", type=int, default=25000)
args = parser.parse_args()
print(prepare(args.input, args.output, args.sample_size))
