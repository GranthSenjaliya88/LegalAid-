import pytest

from app.services.classifier import classify_case_service


@pytest.mark.parametrize(
    ("query", "expected_domain"),
    [
        ("Hospital disclosed my HIV status without consent", "healthcare"),
        ("गर्भपात के लिए मेडिकल टर्मिनेशन ऑफ प्रेग्नेंसी का नियम क्या है", "healthcare"),
        ("Flood disaster relief compensation kaise milega", "public_services"),
        ("देर से जन्म प्रमाणपत्र पंजीकरण कैसे होगा", "public_services"),
        ("Passport application ko refuse kar diya", "public_services"),
        ("भारत में जन्म से नागरिकता कब मिलती है", "constitutional"),
        ("Employer mujhse bonded labour aur forced labour kara raha hai", "human_rights"),
        ("किशोर से hazardous factory में बाल श्रम कराया जा रहा है", "children_rights"),
        ("MSME delayed payment par buyer interest nahi de raha", "livelihood"),
        ("Packaged commodity par legal metrology declaration missing hai", "consumer"),
        ("असुरक्षित भोजन बेचने वाले FSSAI business की शिकायत", "consumer"),
        ("Principal employer contract labour ko safety equipment nahi deta", "labor"),
        ("Pre-litigation mediation agreement enforce kaise hoga", "procedural"),
        ("Partnership firm ke partner ki liability kya hai", "contract"),
        ("Sale of goods me breach of warranty hua", "contract"),
        ("Neighbour ne mera right of way easement block kar diya", "property"),
        ("Public servant ne रिश्वत और undue advantage मांगा", "criminal"),
        ("NDPS narcotic drug offence me bail chahiye", "criminal"),
        ("PMLA money laundering me property attachment hua", "criminal"),
        ("Water pollution control board ko complaint karni hai", "environment"),
        ("Illegal hunting violates wildlife protection law", "environment"),
        ("National Green Tribunal se environmental compensation chahiye", "environment"),
    ],
)
def test_third_expansion_domain_routing(query: str, expected_domain: str):
    assert classify_case_service(query).domain == expected_domain
