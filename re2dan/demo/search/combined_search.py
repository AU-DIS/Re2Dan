import pandas as pd
import ranky as rk

def combineResults(modelResultsOriginal, simpleResults, top_k):
    combinedResults = {'query': modelResultsOriginal['query'], 
                       'department': modelResultsOriginal['department'],
                       'unit': modelResultsOriginal['unit']}
    modelResults = pd.DataFrame(modelResultsOriginal['results'])

    simpleResults = pd.DataFrame(simpleResults['results'])

    # Return model if None from simple
    if len(simpleResults) == 0:
        return modelResultsOriginal
    # Add before model results
    if simpleResults['similarityScore'].mean(axis=0) == -1:
        result = pd.concat([simpleResults, modelResults[~modelResults.documentId.isin(simpleResults.documentId)]])
    # Combine using ranky and short
    else:
        modelResults['modelIndex'] = top_k - modelResults['searchIndex'] + 1
        simpleResults['simpleIndex'] = top_k - simpleResults['searchIndex'] + 1
        ranky_broda_input = modelResults.merge(simpleResults, how='outer')
        ranky_broda = rk.borda(ranky_broda_input[['modelIndex', 'simpleIndex']].fillna(0))
        ranky_broda = ranky_broda.sort_values()
        result = ranky_broda_input.reindex(ranky_broda.index)
        result = result.reset_index(drop=True)
        result['searchIndex'] = result.index + 1
        result = result[['document', 'documentId', 'searchIndex', 'similarityScore', 'url']]
    result = result.head(top_k)

    combinedResults['results'] = result.to_dict('records')

    return combinedResults