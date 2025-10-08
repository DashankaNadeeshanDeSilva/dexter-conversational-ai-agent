# Getting Started with Agent Evaluation

## Prerequisites

Before running your first evaluation, ensure you have:

1. **Environment Variables Set Up**:
   ```bash
   export OPENAI_API_KEY="your-key"
   export MONGODB_URI="mongodb://localhost:27017"
   export PINECONE_API_KEY="your-key"
   export PINECONE_ENVIRONMENT="your-env"
   ```

2. **Dependencies Installed**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Databases Running**:
   - MongoDB (default port 27017)
   - Redis (if using caching)

## Running Your First Evaluation

### Step 1: Test with Small Sample

Start with a small subset to verify everything works:

```bash
cd /path/to/dexter-conversational-ai-agent
python evaluation/run_evaluation.py --dataset benchmark_v1 --max-cases 5 --verbose
```

This will:
- Evaluate 5 test cases from the benchmark dataset
- Show detailed logging with `--verbose`
- Create results in `evaluation/results/`

Expected duration: ~2-5 minutes

### Step 2: Run Full Benchmark

Once the sample works, run the full benchmark:

```bash
python evaluation/run_evaluation.py --dataset benchmark_v1
```

This will:
- Evaluate all 100 test cases
- Generate comprehensive reports
- Update Prometheus metrics (if metrics server is running)

Expected duration: ~30-45 minutes

### Step 3: Start Metrics Server (Optional)

To enable Prometheus metrics:

```bash
# In a separate terminal
python evaluation/metrics_server.py
```

Then access metrics at: `http://localhost:9091/metrics`

### Step 4: View Results

```bash
# List recent results
ls -lt evaluation/results/

# View the latest report (markdown)
cat evaluation/results/report_benchmark_v1_*.md | head -100
```

## Quick Test Checklist

- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] MongoDB accessible
- [ ] Agent initializes without errors
- [ ] Small test run (5 cases) succeeds
- [ ] Full evaluation completes
- [ ] Results files generated
- [ ] Markdown report created

## Troubleshooting First Run

### Issue: "No module named 'evaluation'"

```bash
# Make sure you're in the project root
cd /path/to/dexter-conversational-ai-agent
python evaluation/run_evaluation.py --dataset benchmark_v1
```

### Issue: MongoDB Connection Error

```bash
# Check MongoDB is running
ps aux | grep mongod

# Start MongoDB (macOS)
brew services start mongodb-community

# Start MongoDB (Linux)
sudo systemctl start mongod
```

### Issue: OpenAI API Rate Limit

```bash
# Use smaller batches
python evaluation/run_evaluation.py --dataset benchmark_v1 --max-cases 10

# Wait between runs
sleep 60 && python evaluation/run_evaluation.py --dataset benchmark_v1 --max-cases 10
```

### Issue: "Dataset not found"

```bash
# List available datasets
python evaluation/run_evaluation.py --list-datasets

# Use full path
python evaluation/run_evaluation.py --dataset evaluation/datasets/benchmark_v1.json
```

## Next Steps

After your first successful run:

1. **Establish Baseline**: Save your first results as baseline
2. **Run Edge Cases**: `python evaluation/run_evaluation.py --dataset edge_cases`
3. **Try Conversations**: `python evaluation/run_evaluation.py --dataset multi_turn_conversations`
4. **Set up Monitoring**: Start metrics server and configure Grafana
5. **Regular Evaluation**: Run evaluations before/after major changes

## Expected Results (First Run)

For the benchmark dataset, typical first-run results:

- **Pass Rate**: 70-85%
- **Average Score**: 7.0-8.0
- **Common Issues**:
  - Tool selection accuracy: 80-90%
  - Parameter extraction: 75-85%
  - Edge case handling: 60-70%

Lower scores are expected initially - use them as a baseline for improvement!

## Support

- Full documentation: `evaluation/README.md`
- Report issues or questions in your team channel
- Check verbose logs with `--verbose` flag

---

**Ready to start?** Run the Step 1 command above! 🚀

