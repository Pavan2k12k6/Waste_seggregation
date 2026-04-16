"""
Monitor Training Progress
Shows real-time training metrics from the CSV log
"""

import pandas as pd
import time
import os
from pathlib import Path

def monitor_training(log_file='models/training_log.csv', refresh_interval=10):
    """
    Monitor training progress from CSV log
    
    Args:
        log_file: Path to training log CSV
        refresh_interval: Seconds between updates
    """
    print("=" * 70)
    print("TRAINING PROGRESS MONITOR")
    print("=" * 70)
    print(f"Monitoring: {log_file}")
    print(f"Refresh interval: {refresh_interval} seconds")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 70)
    print()
    
    last_epoch = -1
    
    try:
        while True:
            if Path(log_file).exists():
                df = pd.read_csv(log_file)
                
                if len(df) > last_epoch:
                    # Show new epochs
                    for idx in range(last_epoch + 1, len(df)):
                        row = df.iloc[idx]
                        epoch = idx + 1
                        
                        print(f"\nEpoch {epoch}/{len(df) if 'epoch' not in df.columns else '?'}")
                        print(f"  Train Loss:      {row['loss']:.4f}")
                        print(f"  Train Accuracy:  {row['accuracy']*100:.2f}%")
                        print(f"  Val Loss:        {row['val_loss']:.4f}")
                        print(f"  Val Accuracy:    {row['val_accuracy']*100:.2f}%")
                        
                        # Show improvement
                        if idx > 0:
                            prev_val_loss = df.iloc[idx-1]['val_loss']
                            improvement = prev_val_loss - row['val_loss']
                            if improvement > 0:
                                print(f"  ✓ Val Loss improved by {improvement:.4f}")
                            else:
                                print(f"  ✗ Val Loss increased by {abs(improvement):.4f}")
                    
                    last_epoch = len(df) - 1
                    
                    # Show best metrics so far
                    print("\n" + "-" * 70)
                    print("BEST METRICS SO FAR:")
                    best_val_loss = df['val_loss'].min()
                    best_val_acc = df['val_accuracy'].max()
                    best_loss_epoch = df['val_loss'].idxmin() + 1
                    best_acc_epoch = df['val_accuracy'].idxmax() + 1
                    
                    print(f"  Best Val Loss:     {best_val_loss:.4f} (Epoch {best_loss_epoch})")
                    print(f"  Best Val Accuracy: {best_val_acc*100:.2f}% (Epoch {best_acc_epoch})")
                    print("-" * 70)
                    
            else:
                print(f"Waiting for log file to be created...")
            
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
        print("=" * 70)
        
        if Path(log_file).exists():
            df = pd.read_csv(log_file)
            print("\nFINAL TRAINING SUMMARY:")
            print(f"  Total Epochs:      {len(df)}")
            print(f"  Best Val Loss:     {df['val_loss'].min():.4f}")
            print(f"  Best Val Accuracy: {df['val_accuracy'].max()*100:.2f}%")
            print(f"  Final Val Loss:    {df['val_loss'].iloc[-1]:.4f}")
            print(f"  Final Val Accuracy:{df['val_accuracy'].iloc[-1]*100:.2f}%")
            print("=" * 70)

if __name__ == "__main__":
    monitor_training()
