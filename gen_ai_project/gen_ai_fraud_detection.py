from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from openai import OpenAI
import cohere




# Fraud detection probleminde precision ve recall metrikleri neden kritik öneme sahiptir?
# Bu metriklerin iş maliyetiyle ilişkisini açıklayınız.

# CEVAP:Fraud detection probleminde precision ve recall kritik metriklerdir çünkü sistemin hem yanlış alarm üretme hem de gerçek dolandırıcılık işlemlerini
# yakalama performansını gösterir. Precision, fraud olarak işaretlenen işlemlerin ne kadarının gerçekten fraud olduğunu ifade eder;
# düşük precision, çok sayıda false positive oluşturarak sınırlı olan manuel inceleme kapasitesini gereksiz yere tüketebilir.
# Recall ise gerçek fraud işlemlerinin ne kadarının tespit edildiğini gösterir.
# Bu nedenle recall’ın düşük olması, dolandırıcılık işlemlerinin kaçırılmasına ve doğrudan finansal kayıplara yol açabilecek false negative’lerin artmasına neden olur.
# Bu case’de false negative’lerin maliyetli olması nedeniyle recall önemli olmakla birlikte,
# manuel inceleme kapasitesinin sınırlı olması nedeniyle precision da göz önünde bulundurulmalıdır.
# Dolayısıyla production kararı yalnızca tek bir metriğe göre değil, precision–recall dengesi ve iş maliyetleri birlikte değerlendirilerek verilmelidir.


#  Aşağıdaki hedefleri sağlayan kendi USER PROMPT’unu yazması
# • Bu prompt tüm LLM’lerde aynen kullanılacaktır
# Prompt hedefleri:
# • Production kararı istemeli
# • Metriklerin yanında iş kısıtlarını dikkate almalı
# • Varsayım ve uydurma bilgiyi engellemeli

USER_PROMPT="""Aşağıdaki fraud detection bağlamına göre Logistic Regression, XGBoost ve Zero-shot LLM yaklaşımlarını üretim ortamı için değerlendir.

Precision, recall, false negative/positive maliyetleri, manuel inceleme kapasitesi ve 250 ms latency sınırını dikkate alarak en uygun yaklaşımı seç.

Seçimini gerekçelendir, riskleri ve üretim öncesi gerekli aksiyonları belirt.

Yalnızca verilen bilgileri kullan; varsayım veya bilgi uydurma.

CONTEXT_JSON
{
  "task": "fraud detection (binary classification)",
  "dataset_size": 1800000,
  "fraud_rate": 0.014,
  "models": ["logistic_regression", "xgboost", "zero_shot_llm_classifier"],
  "validation": {
    "logistic_regression": {"precision": 0.81, "recall": 0.22},
    "xgboost": {"precision": 0.74, "recall": 0.61},
    "zero_shot_llm_classifier": {"precision": 0.66, "recall": 0.58}
  },
  "constraints": {
    "false_negatives_costly": true,
    "manual_review_capacity_limited": true,
    "latency_ms_max": 250
  }
}

Temperature değişiminin modelin:
- karar dili,
- risk vurgusu,
- spekülasyon eğilimi

üzerindeki etkisini değerlendir.

"""




def gemini_generate_response(temperature:float,prompt):
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
print(gemini_generate_response(temperature=0.0,prompt=USER_PROMPT))
print("TEMPERATURE = 0.7")
print(gemini_generate_response(temperature=0.7,prompt=USER_PROMPT))



def chat_generate_response(temperature:float,prompt):
    my_key = os.getenv("openai_apikey")

    client2 = OpenAI(api_key=my_key)

    AI_Response = client2.chat.completions.create(
        model="gpt-5.6-luna",
        temperature=temperature,
        messages=[
            {"role": "user", "content": prompt }
        ]
    )

    return AI_Response.choices[0].message.content
print("TEMPERATURE = 0.0")
print(chat_generate_response(temperature=0.0,prompt=USER_PROMPT))
print("TEMPERATURE = 0.7")
print(chat_generate_response(temperature=0.7,prompt=USER_PROMPT))


def cohere_generate_response(temperature:float,prompt):
    my_key = os.getenv("cohere_apikey")

    client = cohere.Client(
        api_key=my_key
    )


    AI_Response = client.chat(
            model = "command",
            temperature=temperature,
            chat_history=[
                {"role": "USER", "message":prompt},
            ],
    )

    return AI_Response.text

print("TEMPERATURE = 0.0")
print(cohere_generate_response(temperature=0.0,prompt=USER_PROMPT))
print("TEMPERATURE = 0.7")
print(cohere_generate_response(temperature=0.7,prompt=USER_PROMPT))


#SORU
# Temperature değişimi, modelin:
# • karar dili,
# • risk vurgusu,
# • ve spekülasyon eğilimi
# üzerinde nasıl bir etki yaratmıştır?


#CEVAP
#Temperature 0.0 seviyesinde model yanıtlarının daha deterministik, kontrollü ve doğrudan karar odaklı olması beklenir.
# Bu seviyede model, verilen precision, recall ve iş kısıtlarına daha sıkı bağlı bir değerlendirme üretir.
# Temperature 0.7'ye yükseltildiğinde ise karar dili daha çeşitli hale gelebilir ve riskler daha farklı biçimlerde ifade edilebilir.
# Bununla birlikte, temperature artışı modelin verilen bilgiler dışına çıkarak varsayım veya spekülasyon üretme eğilimini artırabilir.
# Fraud detection gibi yanlış negatiflerin maliyetli olduğu bir problemde, daha kontrollü ve tutarlı çıktılar nedeniyle düşük
# temperature değerleri karar destek amacıyla daha uygundur.





GÖREV4_USER_PROMPT = """
Aşağıdaki fraud detection context'ini kullanarak production ortamı için nihai bir karar destek değerlendirmesi yap.

Logistic Regression, XGBoost ve Zero-shot LLM yaklaşımlarını karşılaştır ve verilen bilgiler doğrultusunda production için en uygun yaklaşımı seç.

Değerlendirmende özellikle:
- Precision
- Recall
- False negative maliyeti
- False positive maliyeti
- Manuel inceleme kapasitesinin sınırlı olması
- 250 ms maksimum latency sınırı

unsurlarını birlikte dikkate al.

Yalnızca verilen context içerisindeki bilgileri kullan.
Verilmeyen model performansı, latency, maliyet veya başka bir bilgi hakkında varsayım yapma ve bilgi uydurma.
Eğer bir kriter hakkında yeterli bilgi verilmemişse bunu açıkça belirt.

Nihai cevabını aşağıdaki formatta ver:

Model:
Recommendation:
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

Temperature reference range:
- 0.0 - 0.7

Recommendation bölümünde production için seçtiğin yaklaşımı açıkça belirt.
Reasoning bölümünde kararını verilen metrikler ve iş kısıtları üzerinden gerekçelendir.
Risks bölümünde production kararındaki temel riskleri belirt.
Next actions bölümünde production öncesinde yapılması gereken aksiyonları belirt.

Temperature = 0.2 kullanılarak oluşturulan bu final değerlendirmede kesin olmayan bilgileri gerçekmiş gibi sunma.

CONTEXT_JSON
{
  "task": "fraud detection (binary classification)",
  "dataset_size": 1800000,
  "fraud_rate": 0.014,
  "models": [
    "logistic_regression",
    "xgboost",
    "zero_shot_llm_classifier"
  ],
  "validation": {
    "logistic_regression": {
      "precision": 0.81,
      "recall": 0.22
    },
    "xgboost": {
      "precision": 0.74,
      "recall": 0.61
    },
    "zero_shot_llm_classifier": {
      "precision": 0.66,
      "recall": 0.58
    }
  },
  "constraints": {
    "false_negatives_costly": true,
    "manual_review_capacity_limited": true,
    "latency_ms_max": 250
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
