from __future__ import annotations

def build_assistant_response(user_message: str) -> dict[str, object]:
    from app.ml.biobert_predictor import predict_disease_with_confidence
    from app.ml.disease_lookup import get_disease_info
    from app.services.response_service import generate_medical_response

    predicted_disease, confidence = predict_disease_with_confidence(user_message)
    description, precautions = get_disease_info(predicted_disease)
    try:
        from app.rag.retriever import retrieve_context

        rag_chunks = retrieve_context(user_message, k=5)
    except Exception as exc:
        print(f'RAG retrieval failed: {exc}')
        rag_chunks = []

    final_response = generate_medical_response(
        user_symptoms=user_message,
        predicted_disease=predicted_disease,
        description=description,
        precautions=precautions,
        rag_chunks=rag_chunks,
        confidence=confidence,
    )
    return {
        'predicted_disease': predicted_disease,
        'confidence': confidence,
        'description': description,
        'precautions': precautions,
        'rag_chunks': rag_chunks,
        'response_text': final_response,
    }
