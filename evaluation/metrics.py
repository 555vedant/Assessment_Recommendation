def recall_at_k(true_urls, pred_urls, k=10):
    return len(set(true_urls) & set(pred_urls[:k])) / len(true_urls)
