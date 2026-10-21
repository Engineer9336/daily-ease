from .i18n import t

def answer(question: str, lang: str = "en") -> str:
    q=question.lower()
    if any(x in q for x in ["find", "search", "worker", "service", "वर्कर", "सेवा", "dhoond"]):
        return {"en":"Open Explore Services, enter a service or skill, then optionally filter by category and locality. Open a worker card to request help.","hi":"सेवाएँ देखें खोलें, सेवा या कौशल लिखें और चाहें तो श्रेणी व इलाके से फ़िल्टर करें। मदद माँगने के लिए वर्कर प्रोफ़ाइल खोलें।","hinglish":"Explore Services kholo, service ya skill likho aur category/locality se filter karo. Help maangne ke liye worker card kholo."}.get(lang,"Open Explore Services and search by skill or locality.")
    if any(x in q for x in ["register", "photo", "profile", "रजिस्टर", "फोटो", "upload", "profile"]):
        return {"en":"Choose Become a Worker and create a worker account. Complete your category, skills, locality and profile details. In My profile, JPG/PNG photos up to 5 MB can be uploaded.","hi":"वर्कर बनें चुनें और खाता बनाएँ। श्रेणी, कौशल, इलाका और प्रोफ़ाइल विवरण भरें। मेरी प्रोफ़ाइल में 5 MB तक JPG/PNG फोटो अपलोड कर सकते हैं।","hinglish":"Become a Worker select karke account banao. Category, skills, locality aur profile details bharo. My profile mein 5 MB tak JPG/PNG photo upload kar sakte ho."}.get(lang, "Choose Become a Worker and complete your profile.")
    if any(x in q for x in ["request", "booking", "status", "अनुरोध", "स्थिति", "request"]):
        return {"en":"Open a worker profile and submit the service description, location and preferred time. Track progress in Service requests. Only the assigned worker can accept or update the job.","hi":"वर्कर प्रोफ़ाइल खोलकर काम का विवरण, स्थान और पसंदीदा समय भरें। सेवा अनुरोध में स्थिति देखें। केवल संबंधित वर्कर काम स्वीकार या अपडेट कर सकता है।","hinglish":"Worker profile kholo aur kaam ka detail, location aur preferred time bharo. Service requests mein status track karo. Assigned worker hi job accept/update kar sakta hai."}.get(lang, "Open a worker profile to send a request.")
    if any(x in q for x in ["language", "भाषा", "hindi", "hinglish"]):
        return {"en":"Use the Language selector in the sidebar. Choose English, हिन्दी or Hinglish; the page updates immediately.","hi":"साइडबार में भाषा चुनें। English, हिन्दी या Hinglish चुनने पर पेज तुरंत अपडेट होगा।","hinglish":"Sidebar mein Language selector se English, हिन्दी ya Hinglish choose karo. Page turant update hoga."}.get(lang, "Use the language selector in the sidebar.")
    return t("unknown", lang)
