import os
import json
import matplotlib.pyplot as plt
import seaborn as sns

def plot_performance(results_folder='evaluation/json_results', include_methods=None, colors=None):
    # Set default colors
    default_colors = ['skyblue', 'lightgreen', 'salmon']
    if colors is None:
        colors = default_colors
    
    # Load JSON files
    results = []
    for filename in os.listdir(results_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(results_folder, filename)
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                    if 'name' not in data:
                        print(f"Warning: {filename} does not contain a 'name' field. Skipping.")
                        continue
                    if include_methods is None or data['name'] in include_methods:
                        results.append(data)
                except json.JSONDecodeError:
                    print(f"Warning: {filename} is not a valid JSON file. Skipping.")
    
    if not results:
        print("No JSON files found with matching 'name' fields.")
        return
    
    # Validate data
    required_metrics = ["average_precision", "average_recall", "average_f1", "average_mrr", "end_to_end_accuracy"]
    for result in results.copy():
        if not all(metric in result for metric in required_metrics):
            print(f"Warning: {result['name']} is missing some required metrics. Skipping.")
            results.remove(result)
    
    if not results:
        print("No valid results remaining after validation.")
        return
    
    # Sort results based on end-to-end accuracy
    results.sort(key=lambda x: x['end_to_end_accuracy'])
    
    # Prepare data for plotting
    methods = [result['name'] for result in results]
    metrics = required_metrics
    
    # Set up the plot
    plt.figure(figsize=(14, 6))
    sns.set_style("whitegrid")
    
    x = range(len(metrics))
    width = 0.8 / len(results)
    
    # Create color palette
    num_methods = len(results)
    color_palette = colors[:num_methods] + sns.color_palette("husl", num_methods - len(colors))
    
    # Plot bars for each method
    for i, (result, color) in enumerate(zip(results, color_palette)):
        values = [result[metric] for metric in metrics]
        offset = (i - len(results)/2 + 0.5) * width
        bars = plt.bar([xi + offset for xi in x], values, width, label=result['name'], color=color)
        
        # Add value labels on the bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.2f}', ha='center', va='bottom', fontsize=8)
    
    # Customize the plot
    plt.xlabel('Metrics', fontsize=12)
    plt.ylabel('Values', fontsize=12)
    plt.title('RAG Performance Metrics (Sorted by End-to-End Accuracy)', fontsize=16)
    plt.xticks(x, metrics, rotation=45, ha='right')
    plt.legend(title='Methods', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.ylim(0, 1)
    
    plt.tight_layout()
    plt.show()
