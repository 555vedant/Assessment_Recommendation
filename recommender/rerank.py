def balance(indices, df, max_results=10):
    hard = []
    soft = []

    for idx in indices:
        ttype = str(df.iloc[idx]["test_type"]).lower()
        if "knowledge" in ttype or "skill" in ttype:
            hard.append(idx)
        elif "personality" in ttype or "behavior" in ttype:
            soft.append(idx)

    final = hard[:5] + soft[:5]
    if len(final) < max_results:
        final += [i for i in indices if i not in final][:max_results-len(final)]

    return final[:max_results]
