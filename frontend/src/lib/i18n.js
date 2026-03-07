// frontend/src/lib/i18n.js
// ─────────────────────────────────────────────────────────────────
// Lightweight translation map for SamvaadAI UI labels.
//
// Rules:
//   • No heavy i18n framework — plain JS lookup
//   • Fallback: selected lang → English → raw key
//   • Supports: en, hi, mr
// ─────────────────────────────────────────────────────────────────

export const translations = {
    en: {
        // Results page
        results_title: "Eligibility Results",
        results_subtitle: "Based on your profile, here are the government schemes matched for you.",
        eligible_label: "Eligible Schemes",
        partial_label: "Partially Eligible",
        ineligible_label: "Not Eligible",
        view_results: "View Results",
        no_results: "No eligibility data yet. Start a conversation to discover schemes.",
        go_to_chat: "Start Conversation",
        benefit: "Benefit",
        apply_now: "Apply Now",
        missing_fields: "Missing Information",
        guidance: "What You Need",
        reasons: "Reason",
        scheme_details: "Scheme Details",
        back_to_results: "Back to Results",
        proceed_to_apply: "Proceed to Official Application",
        disclaimer: "SamvaadAI facilitates discovery but does not process payments.",
        // Chat
        new_conversation: "New",
        processing: "Processing...",
        assistant_active: "Assistant Active",
        tap_to_speak: "Tap to Speak",
        listening: "Listening...",
        tell_about_yourself: "Tell me about yourself...",
        waiting_for_response: "Waiting for response...",
        analysis_complete: "Analysis Complete",
        profile_match: "Profile Match",
        // Common
        overview: "Overview",
        chat: "Chat",
        results: "Results",
        language: "Language",
        continue_conversation: "Continue Conversation",
        try_again: "Try again",
        scheme_not_found: "Scheme not found",
        scheme_not_found_desc: "The scheme details could not be located. Please try viewing your results again.",
        eligible_schemes: "Eligible Schemes",
        required_documents: "Required Documents",
        low_confidence_prompt: "I didn't catch that clearly. Could you please repeat?",
        check_eligibility: "Check Eligibility",
    },

    hi: {
        results_title: "पात्रता परिणाम",
        results_subtitle: "आपकी प्रोफ़ाइल के आधार पर, ये सरकारी योजनाएँ आपके लिए मिली हैं।",
        eligible_label: "पात्र योजनाएँ",
        partial_label: "आंशिक रूप से पात्र",
        ineligible_label: "पात्र नहीं",
        view_results: "परिणाम देखें",
        no_results: "अभी कोई पात्रता डेटा नहीं है। योजनाएँ खोजने के लिए बातचीत शुरू करें।",
        go_to_chat: "बातचीत शुरू करें",
        benefit: "लाभ",
        apply_now: "अभी आवेदन करें",
        missing_fields: "अनुपलब्ध जानकारी",
        guidance: "आपको क्या चाहिए",
        reasons: "कारण",
        scheme_details: "योजना विवरण",
        back_to_results: "परिणामों पर वापस",
        proceed_to_apply: "आधिकारिक आवेदन पर जाएं",
        disclaimer: "SamvaadAI खोज में मदद करता है लेकिन भुगतान प्रक्रिया नहीं करता।",
        new_conversation: "नया",
        processing: "प्रक्रिया हो रही है...",
        assistant_active: "सहायक सक्रिय",
        tap_to_speak: "बोलने के लिए टैप करें",
        listening: "सुन रहे हैं...",
        tell_about_yourself: "अपने बारे में बताएं...",
        waiting_for_response: "प्रतिक्रिया की प्रतीक्षा...",
        analysis_complete: "विश्लेषण पूर्ण",
        profile_match: "प्रोफ़ाइल मिलान",
        overview: "अवलोकन",
        chat: "चैट",
        results: "परिणाम",
        language: "भाषा",
        continue_conversation: "बातचीत जारी रखें",
        try_again: "पुनः प्रयास करें",
        scheme_not_found: "योजना नहीं मिली",
        scheme_not_found_desc: "योजना का विवरण नहीं मिल सका। कृपया अपने परिणाम फिर से देखें।",
        eligible_schemes: "पात्र योजनाएँ",
        required_documents: "आवश्यक दस्तावेज़",
        low_confidence_prompt: "मुझे स्पष्ट रूप से समझ नहीं आया। कृपया दोहराएं?",
        check_eligibility: "पात्रता जाँचें",
    },

    mr: {
        results_title: "पात्रता निकाल",
        results_subtitle: "तुमच्या प्रोफाइलच्या आधारावर, या सरकारी योजना तुमच्यासाठी जुळल्या आहेत.",
        eligible_label: "पात्र योजना",
        partial_label: "अंशतः पात्र",
        ineligible_label: "अपात्र",
        view_results: "निकाल पहा",
        no_results: "अजून पात्रता डेटा नाही. योजना शोधण्यासाठी संवाद सुरू करा.",
        go_to_chat: "संवाद सुरू करा",
        benefit: "लाभ",
        apply_now: "आता अर्ज करा",
        missing_fields: "गहाळ माहिती",
        guidance: "तुम्हाला काय हवे",
        reasons: "कारण",
        scheme_details: "योजना तपशील",
        back_to_results: "निकालांवर परत",
        proceed_to_apply: "अधिकृत अर्जावर जा",
        disclaimer: "SamvaadAI शोधात मदत करते पण पैसे प्रक्रिया करत नाही.",
        new_conversation: "नवीन",
        processing: "प्रक्रिया होत आहे...",
        assistant_active: "सहाय्यक सक्रिय",
        tap_to_speak: "बोलण्यासाठी टॅप करा",
        listening: "ऐकत आहे...",
        tell_about_yourself: "तुमच्याबद्दल सांगा...",
        waiting_for_response: "प्रतिसादाची वाट...",
        analysis_complete: "विश्लेषण पूर्ण",
        profile_match: "प्रोफाइल जुळणी",
        overview: "आढावा",
        chat: "चॅट",
        results: "निकाल",
        language: "भाषा",
        continue_conversation: "संवाद सुरू ठेवा",
        try_again: "पुन्हा प्रयत्न करा",
        scheme_not_found: "योजना सापडली नाही",
        scheme_not_found_desc: "योजनेचा तपशील सापडला नाही. कृपया तुमचे निकाल पुन्हा पहा.",
        eligible_schemes: "पात्र योजना",
        required_documents: "आवश्यक कागदपत्रे",
        low_confidence_prompt: "मला स्पष्टपणे समजले नाही. कृपया पुन्हा सांगा?",
        check_eligibility: "पात्रता तपासा",
    },
};

/**
 * Translate a key into the selected language.
 *
 * Fallback chain: lang → en → raw key
 *
 * @param {string} key   - Translation key
 * @param {string} lang  - Language code (en, hi, mr)
 * @returns {string}
 */
export function t(key, lang = "en") {
    return translations[lang]?.[key] ?? translations.en?.[key] ?? key;
}
