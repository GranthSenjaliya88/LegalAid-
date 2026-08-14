import pytest

from app.services.classifier import classify_case_service


@pytest.mark.parametrize(
    ("query", "expected_domain"),
    [
        ("I need to challenge an arbitral award in court", "contract"),
        ("लोक सूचना अधिकारी ने मेरे आरटीआई आवेदन का जवाब नहीं दिया", "public_services"),
        ("मानसिक स्वास्थ्य सेवा में मेरे साथ भेदभाव हुआ", "healthcare"),
        ("ट्रांसजेंडर व्यक्ति को नौकरी में भेदभाव सहना पड़ा", "human_rights"),
        ("नाबालिग की शादी रोकने के लिए court order चाहिए", "children_rights"),
        ("शादी में दहेज मांग रहे हैं", "women_rights"),
        ("Court se minor ka guardian appoint karana hai", "family"),
        ("तीन तलाक के बाद allowance kaise milega", "women_rights"),
        ("Financial creditor wants to start IBC insolvency", "insolvency"),
        ("बिजली कनेक्शन देने से मना कर दिया", "consumer"),
        ("संपत्ति दस्तावेज पंजीकरण की deadline क्या है", "property"),
        ("राशन नहीं मिला और खाद्य सुरक्षा भत्ता चाहिए", "public_services"),
        ("रेहड़ी पटरी विक्रेता को बिना survey हटा दिया", "livelihood"),
        ("मानवाधिकार आयोग में complaint करनी है", "human_rights"),
        ("कारखाना प्रदूषण और जहरीले कचरे की शिकायत है", "environment"),
        ("Aadhaar authentication fail होने से subsidy रोकी", "public_services"),
    ],
)
def test_second_expansion_domain_routing(query: str, expected_domain: str):
    assert classify_case_service(query).domain == expected_domain
