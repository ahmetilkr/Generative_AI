from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from openai import OpenAI
import cohere

#SORU
# Bu senaryoda LSTM modeli ile LLM’in rolleri neden net bir şekilde ayrılmalıdır?
# LLM’in doğrudan tahmin üreten bir model olarak kullanılması hangi riskleri doğurur?

#CEVAP
# LSTM modeli zaman serisi verilerinden öğrenerek temel satış tahminini üretmelidir.
# LLM ise bu tahmini bağlamsal bilgiler ışığında yorumlayan ve gerekçelendiren
# bir karar destek katmanı olarak kullanılmalıdır.
#
# Bu rollerin ayrılması önemlidir çünkü LSTM sayısal zaman serisi tahmini için
# ana model olarak konumlandırılmıştır. LLM'in doğrudan tahmin üretmesi ise
# deterministik olmayan ve dil tabanlı bir sistemin iş kritik satış kararlarında
# doğrudan kullanılmasına neden olabilir.
#
# Özellikle stok planlama, lojistik, kampanya bütçeleri ve tedarikçi anlaşmaları
# gibi iş kritik kararlar nedeniyle LLM'in nihai kararı tek başına vermemesi ve
# Human-in-the-Loop yapısında insan onayının bulunması gerekir.


USER_PROMPT = """
Aşağıdaki sales forecast adjustment context'ini kullanarak mevcut LSTM satış
tahminini değerlendir.

LSTM tarafından üretilen 30 günlük satış tahmininin bağlamsal bilgiler
açısından ayarlanmasının gerekip gerekmediğini değerlendir.

Değerlendirmeni:
- mevcut LSTM tahmininin performansı,
- SMAPE değerleri,
- özel günler,
- ani kampanyalar,
- dışsal olaylar,
- açıklanabilirlik gereksinimi,
- insan onayı gerekliliği
çerçevesinde yap.

LLM olarak yeni bir satış tahmini üretme ve LSTM tahmininin yerine geçme.
Yalnızca mevcut tahmini değerlendir ve adjustment gerekip gerekmediğini
belirt.

Kararını açık ve açıklanabilir bir gerekçeyle destekle.

Yalnızca verilen context içerisindeki bilgileri kullan.
Verilmeyen bilgiler hakkında varsayım yapma veya bilgi uydurma.
Bir kriter hakkında yeterli bilgi yoksa bunu açıkça belirt.

CONTEXT_JSON {
  "task": "sales forecast adjustment support",
  "dataset_size": 95000,
  "base_model": "lstm_time_series",
  "forecast_horizon_days": 30,
  "evaluation_metric": "smape",
  "base_model_smape": 13.2,
  "llm_adjusted_smape": 12.6,
  "constraints": {
    "human_approval_required": true,
    "explainability_required": true,
    "business_critical_decisions": true
  }
}
"""


def gemini_generate_response(temperature: float, prompt):
    load_dotenv()

    my_key = os.getenv("google_apikey")

    client = genai.Client(api_key=my_key)

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature
        )
    )

    return response.text


print("TEMPERATURE = 0.0")
print(gemini_generate_response(temperature=0.0, prompt=USER_PROMPT))
print("TEMPERATURE = 0.7")
print(gemini_generate_response(temperature=0.7, prompt=USER_PROMPT))


def chat_generate_response(temperature: float, prompt):
    my_key = os.getenv("openai_apikey")

    client2 = OpenAI(api_key=my_key)

    AI_Response = client2.chat.completions.create(
        model="gpt-5.6-luna",
        temperature=temperature,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return AI_Response.choices[0].message.content


print("TEMPERATURE = 0.0")
print(chat_generate_response(temperature=0.0, prompt=USER_PROMPT))
print("TEMPERATURE = 0.7")
print(chat_generate_response(temperature=0.7, prompt=USER_PROMPT))


def cohere_generate_response(temperature: float, prompt):
    my_key = os.getenv("cohere_apikey")

    client = cohere.Client(
        api_key=my_key
    )

    AI_Response = client.chat(
        model="command",
        temperature=temperature,
        chat_history=[
            {"role": "USER", "message": prompt},
        ],
    )

    return AI_Response.text


print("TEMPERATURE = 0.0")
print(cohere_generate_response(temperature=0.0, prompt=USER_PROMPT))
print("TEMPERATURE = 0.7")
print(cohere_generate_response(temperature=0.7, prompt=USER_PROMPT))



# Temperature 0.0 seviyesinde model yanıtları daha tutarlı ve doğrudan
# olurken, verilen context'e daha sıkı bağlı kalma eğilimi göstermiştir.
#
# Temperature 0.7 seviyesinde gerekçelendirme biçimi daha çeşitli hale
# gelmiş ve belirsizlikler farklı şekillerde ifade edilmiştir. Bununla
# birlikte daha yüksek temperature, verilen bilgiler üzerinden daha fazla
# yorum yapılmasına ve aşırı yorum riskinin artmasına neden olabilir.
#
# Bu case'de satış tahminleri stok, lojistik, kampanya bütçeleri ve tedarikçi
# kararları gibi business-critical kararları etkilediği için kontrollü ve
# açıklanabilir çıktılar önemlidir.



GÖREV4_USER_PROMPT = """
Aşağıdaki sales forecast adjustment context'ini kullanarak production ortamı
için nihai bir karar destek değerlendirmesi yap.

LSTM modelinin ana tahmin üreticisi, LLM'in ise tahmini yorumlayan ve
adjustment gerekip gerekmediğini değerlendiren bir karar destek katmanı
olduğunu dikkate al.

Production ortamında LLM destekli adjustment yaklaşımının kullanılıp
kullanılmaması konusunda bir recommendation ver.

Değerlendirmeni özellikle şu unsurlar üzerinden yap:
- Base model SMAPE
- LLM adjusted SMAPE
- Human approval gerekliliği
- Explainability gerekliliği
- Business-critical decisions
- LLM'in tahmin üretmek yerine karar destek rolünde olması

Yalnızca verilen context içerisindeki bilgileri kullan.
Verilmeyen bilgiler hakkında varsayım yapma veya bilgi uydurma.
Bir kriter hakkında yeterli bilgi verilmemişse bunu açıkça belirt.

Cevabını tam olarak şu formatta ver:

Recommendation:
[Production kararı]

Reasoning:
- Madde 1
- Madde 2
- Madde 3

Risks:
- Risk 1
- Risk 2

Next actions:
- Aksiyon 1
- Aksiyon 2

CONTEXТ_JSON {
  "task": "sales forecast adjustment support",
  "dataset_size": 95000,
  "base_model": "lstm_time_series",
  "forecast_horizon_days": 30,
  "evaluation_metric": "smape",
  "base_model_smape": 13.2,
  "llm_adjusted_smape": 12.6,
  "constraints": {
    "human_approval_required": true,
    "explainability_required": true,
    "business_critical_decisions": true
  }
}
"""

FINAL_TEMPERATURE = 0.2

print("\n" + "=" * 60)
print("GEMINI - FINAL PRODUCTION DECISION")
print("=" * 60)

print(gemini_generate_response(
    temperature=FINAL_TEMPERATURE,
    prompt=GÖREV4_USER_PROMPT
))


print("\n" + "=" * 60)
print("GPT - FINAL PRODUCTION DECISION")
print("=" * 60)

print(chat_generate_response(
    temperature=FINAL_TEMPERATURE,
    prompt=GÖREV4_USER_PROMPT
))


print("\n" + "=" * 60)
print("COHERE - FINAL PRODUCTION DECISION")
print("=" * 60)

print(cohere_generate_response(
    temperature=FINAL_TEMPERATURE,
    prompt=GÖREV4_USER_PROMPT
))

