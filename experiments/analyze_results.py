#!/usr/bin/env python3
"""
RAG Experiment Results Analysis
Generate tuning_report_v1.md from grid search results
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import List, Dict, Any

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

def load_latest_results() -> pd.DataFrame:
    """Load the most recent grid search results CSV"""
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    
    # Find the most recent CSV file
    csv_files = [f for f in os.listdir(results_dir) if f.startswith("grid_search_")]
    if not csv_files:
        raise FileNotFoundError("No grid search results found")
    
    latest_file = max(csv_files)
    file_path = os.path.join(results_dir, latest_file)
    
    print(f"Loading results from: {latest_file}")
    df = pd.read_csv(file_path)
    return df

def get_best_parameters(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Get top N parameter combinations by recall@5"""
    best_params = df.nlargest(n, 'recall@5')[['chunk', 'k', 'temp', 'recall@5', 'f1', 'latency_ms', 'cost_cents']]
    return best_params

def create_performance_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Create performance summary statistics"""
    summary = {
        'total_experiments': len(df),
        'avg_recall': df['recall@5'].mean(),
        'avg_f1': df['f1'].mean(),
        'avg_latency': df['latency_ms'].mean(),
        'avg_cost': df['cost_cents'].mean(),
        'best_recall': df['recall@5'].max(),
        'worst_recall': df['recall@5'].min(),
        'perfect_recalls': len(df[df['recall@5'] == 1.0]),
        'failed_recalls': len(df[df['recall@5'] == 0.0])
    }
    return summary

def generate_insights(df: pd.DataFrame) -> List[str]:
    """Generate insights from the results"""
    insights = []
    
    # Chunk size analysis
    chunk_256 = df[df['chunk'] == 256]
    chunk_512 = df[df['chunk'] == 512]
    
    if chunk_256['recall@5'].mean() > chunk_512['recall@5'].mean():
        insights.append("**Chunk size 256** shows better average recall than 512")
    else:
        insights.append("**Chunk size 512** shows better average recall than 256")
    
    # Top-k analysis
    k_analysis = df.groupby('k')['recall@5'].mean()
    best_k = k_analysis.idxmax()
    insights.append(f"**Top-k={best_k}** performs best on average")
    
    # Temperature analysis
    temp_analysis = df.groupby('temp')['recall@5'].mean()
    best_temp = temp_analysis.idxmax()
    insights.append(f"**Temperature={best_temp}** shows best average performance")
    
    # Cost analysis
    cost_performance = df.groupby(['chunk', 'k'])['cost_cents'].mean()
    most_efficient = cost_performance.idxmin()
    insights.append(f"**Most cost-efficient**: chunk={most_efficient[0]}, k={most_efficient[1]}")
    
    return insights

def create_visualizations(df: pd.DataFrame, output_dir: str):
    """Create visualization plots"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Recall by parameters
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Recall by chunk size
    df.boxplot(column='recall@5', by='chunk', ax=axes[0,0])
    axes[0,0].set_title('Recall@5 by Chunk Size')
    axes[0,0].set_xlabel('Chunk Size')
    axes[0,0].set_ylabel('Recall@5')
    
    # Recall by top-k
    df.boxplot(column='recall@5', by='k', ax=axes[0,1])
    axes[0,1].set_title('Recall@5 by Top-k')
    axes[0,1].set_xlabel('Top-k')
    axes[0,1].set_ylabel('Recall@5')
    
    # Recall by temperature
    df.boxplot(column='recall@5', by='temp', ax=axes[1,0])
    axes[1,0].set_title('Recall@5 by Temperature')
    axes[1,0].set_xlabel('Temperature')
    axes[1,0].set_ylabel('Recall@5')
    
    # Cost vs Performance scatter
    axes[1,1].scatter(df['cost_cents'], df['recall@5'], alpha=0.6)
    axes[1,1].set_xlabel('Cost (cents)')
    axes[1,1].set_ylabel('Recall@5')
    axes[1,1].set_title('Cost vs Performance')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'performance_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()

def generate_report(df: pd.DataFrame, best_params: pd.DataFrame, 
                   summary: Dict[str, Any], insights: List[str]) -> str:
    """Generate the tuning report markdown"""
    
    report = f"""# RAG Experiment Tuning Report v1

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Experiments**: {summary['total_experiments']}  
**Data Source**: {df['run_id'].iloc[0][:8]}... (latest grid search)

## Executive Summary

- **Best Average Recall@5**: {summary['avg_recall']:.3f}
- **Best Average F1 Score**: {summary['avg_f1']:.3f}
- **Average Latency**: {summary['avg_latency']:.1f}ms
- **Average Cost**: ${summary['avg_cost']:.4f}
- **Perfect Scores**: {summary['perfect_recalls']} experiments
- **Failed Experiments**: {summary['failed_recalls']} experiments

## Top 5 Parameter Combinations

| Rank | Chunk | Top-k | Temp | Recall@5 | F1 | Latency(ms) | Cost(cents) |
|------|-------|-------|------|----------|----|-------------|-------------|
"""

    for i, (_, row) in enumerate(best_params.iterrows(), 1):
        report += f"| {i} | {row['chunk']} | {row['k']} | {row['temp']} | {row['recall@5']:.3f} | {row['f1']:.3f} | {row['latency_ms']:.1f} | {row['cost_cents']:.4f} |\n"

    report += f"""
## Key Insights

"""

    for insight in insights:
        report += f"- {insight}\n"

    report += f"""
## Performance Analysis

### Best Parameters
**Optimal Configuration**: chunk={best_params.iloc[0]['chunk']}, k={best_params.iloc[0]['k']}, temp={best_params.iloc[0]['temp']}

**Why this works best**:
- Achieves {best_params.iloc[0]['recall@5']:.1%} recall with {best_params.iloc[0]['f1']:.1%} F1 score
- Cost-effective at ${best_params.iloc[0]['cost_cents']:.4f} per query
- Reasonable latency of {best_params.iloc[0]['latency_ms']:.0f}ms

### Cost-Performance Trade-off
- **Most Expensive**: ${df['cost_cents'].max():.4f} (chunk={df.loc[df['cost_cents'].idxmax(), 'chunk']}, k={df.loc[df['cost_cents'].idxmax(), 'k']})
- **Cheapest**: ${df['cost_cents'].min():.4f} (chunk={df.loc[df['cost_cents'].idxmin(), 'chunk']}, k={df.loc[df['cost_cents'].idxmin(), 'k']})
- **Best Value**: ${best_params.iloc[0]['cost_cents']:.4f} with {best_params.iloc[0]['recall@5']:.1%} recall

## Recommendations

1. **Production Use**: chunk={best_params.iloc[0]['chunk']}, k={best_params.iloc[0]['k']}, temp={best_params.iloc[0]['temp']}
2. **Cost Optimization**: Consider chunk={df.loc[df['cost_cents'].idxmin(), 'chunk']}, k={df.loc[df['cost_cents'].idxmin(), 'k']} for high-volume scenarios
3. **Performance Focus**: Use chunk={df.loc[df['recall@5'].idxmax(), 'chunk']}, k={df.loc[df['recall@5'].idxmax(), 'k']} for critical applications

## Next Steps

- Implement the recommended parameters in production
- Monitor real-world performance vs. experimental results
- Consider A/B testing different configurations
- Plan for scaling experiments with larger datasets
"""
    
    return report

def main():
    """Main analysis function"""
    print("Loading experiment results...")
    df = load_latest_results()
    
    print("Analyzing results...")
    best_params = get_best_parameters(df)
    summary = create_performance_summary(df)
    insights = generate_insights(df)
    
    print("Creating visualizations...")
    output_dir = os.path.join(os.path.dirname(__file__), "results")
    create_visualizations(df, output_dir)
    
    print("Generating report...")
    report = generate_report(df, best_params, summary, insights)
    
    # Save report
    report_path = os.path.join(output_dir, "tuning_report_v1.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Report saved to: {report_path}")
    print(f"Visualizations saved to: {output_dir}/performance_analysis.png")
    
    # Print summary
    print("\n=== ANALYSIS SUMMARY ===")
    print(f"Total experiments: {summary['total_experiments']}")
    print(f"Average recall: {summary['avg_recall']:.3f}")
    print(f"Best recall: {summary['best_recall']:.3f}")
    print(f"Perfect scores: {summary['perfect_recalls']}")
    print(f"Failed experiments: {summary['failed_recalls']}")

if __name__ == "__main__":
    main() 