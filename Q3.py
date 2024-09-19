from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask("KarbonCard Q3 Sentiment API")

sentiment_pipeline = pipeline(
    "sentiment-analysis", 
    model="cardiffnlp/twitter-roberta-base-sentiment"
)

label_mapping = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive"
}

# model is not fine-tuned for this dataset, Hence here I am thresholding it
HIGH_CONFIDENCE_THRESHOLD = 0.7
LOW_CONFIDENCE_THRESHOLD = 0.4

# Define the endpoint for processing reviews
@app.route('/analyze', methods=['POST'])
def analyze_reviews():
    if not request.is_json:
        return jsonify({"error": "Invalid input, JSON expected."}), 400
    
    data = request.get_json()
    
    if not isinstance(data, list):
        return jsonify({"error": "Expected a list of review objects."}), 400

    results = []
    for review in data:
        try:
            review_text = review.get("review_text")
            product_id = review.get("product_id")
            review_id = review.get("review_id")
            expected_sentiment = review.get("expected_sentiment", "unknown")

            if not review_text:
                results.append({
                    "product_id": product_id,
                    "review_id": review_id,
                    "error": "Missing review text."
                })
                continue

            analysis = sentiment_pipeline(review_text)[0]
            predicted_label = analysis['label']
            sentiment = label_mapping.get(predicted_label, "unknown")  # As per input label
            score = analysis['score']

            if score < LOW_CONFIDENCE_THRESHOLD:
                sentiment = "neutral"
            elif LOW_CONFIDENCE_THRESHOLD <= score < HIGH_CONFIDENCE_THRESHOLD:
                # Moderate confidence 
                sentiment = "neutral" if sentiment == "positive" or sentiment == "negative" else sentiment

            # Output
            response = {
                "product_id": product_id,
                "review_id": review_id,
                "review_text": review_text,
                "expected_sentiment": expected_sentiment,
                "predicted_sentiment": sentiment,
                "confidence_score": score
            }
            results.append(response)

        except Exception as e:
            results.append({
                "product_id": review.get("product_id", "unknown"),
                "review_id": review.get("review_id", "unknown"),
                "error": str(e)
            })

    # Return result in JSON format
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
