from __future__ import annotations

from collections.abc import Mapping

from app.core.config import get_settings

SupportedLanguage = str


LANGUAGE_ALIASES: dict[str, SupportedLanguage] = {
    "fa": "fa",
    "fa-ir": "fa",
    "fa-af": "fa",
    "persian": "fa",
    "farsi": "fa",
    "en": "en",
    "en-us": "en",
    "en-gb": "en",
    "english": "en",
    "ar": "ar",
    "ar-sa": "ar",
    "ar-ae": "ar",
    "arabic": "ar",
    "tr": "tr",
    "tr-tr": "tr",
    "turkish": "tr",
}


MESSAGES: dict[str, Mapping[SupportedLanguage, str]] = {
    "start": {
        "fa": "بسم الله الرحمن الرحیم\n\nبه ربات قرآن ناطق خوش آمدید.\n\nاین ربات برای ارسال و نمایش محتوای قرآنی طراحی شده است و می‌تواند آیات تصادفی را به‌همراه ترجمه برای شما ارسال کند.\n\nاز منوی پایین می‌توانید مستقیماً «آیه تصادفی» را انتخاب کنید. همچنین با دستور /random یک آیه تصادفی دریافت می‌کنید و با /help فهرست فرمان‌ها را می‌بینید.",
        "en": "In the name of Allah, the Most Compassionate, the Most Merciful\n\nWelcome to Natiq Quran Bot.\n\nThis bot is designed to deliver and display Quranic content and can send you random ayahs together with their translations.\n\nUse the menu below to choose Random Ayah directly. You can also use /random to receive a random ayah and /help to view the command list.",
        "ar": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\n\nمرحبًا بك في بوت ناطق للقرآن.\n\nصُمم هذا البوت لعرض وإرسال المحتوى القرآني، ويمكنه إرسال آيات عشوائية مع ترجمتها.\n\nيمكنك استخدام القائمة بالأسفل لاختيار الآية العشوائية مباشرة، كما يمكنك استخدام /random للحصول على آية عشوائية و /help لعرض قائمة الأوامر.",
        "tr": "Rahman ve Rahim olan Allah'ın adıyla\n\nNatiq Kur'an Botuna hoş geldiniz.\n\nBu bot Kur'an içeriğini sunmak ve göstermek için tasarlanmıştır; size çevirileriyle birlikte rastgele ayetler gönderebilir.\n\nAşağıdaki menüden doğrudan Rastgele Ayet seçebilirsiniz. Ayrıca rastgele bir ayet almak için /random ve komut listesini görmek için /help kullanabilirsiniz.",
    },
    "surah_label": {
        "fa": "سوره",
        "en": "Surah",
        "ar": "سورة",
        "tr": "Sure",
    },
    "translation_label": {
        "fa": "📝",
        "en": "📝",
        "ar": "📝",
        "tr": "📝",
    },
    "main_menu_random_button": {
        "fa": "آیه تصادفی",
        "en": "Random Ayah",
        "ar": "آية عشوائية",
        "tr": "Rastgele Ayet",
    },
    "main_menu_admin_button": {
        "fa": "تنظیمات ادمین",
        "en": "Admin Settings",
        "ar": "إعدادات المشرف",
        "tr": "Yönetici Ayarları",
    },
    "next_ayah_button": {
        "fa": "آیه بعدی",
        "en": "Next Ayah",
        "ar": "الآية التالية",
        "tr": "Sonraki Ayet",
    },
    "random_ayah_error": {
        "fa": "خطا در دریافت آیه.",
        "en": "Failed to fetch the ayah.",
        "ar": "تعذر جلب الآية.",
        "tr": "Ayet alınamadı.",
    },
    "next_ayah_error": {
        "fa": "خطا در دریافت آیه",
        "en": "Failed to fetch the ayah",
        "ar": "تعذر جلب الآية",
        "tr": "Ayet alınamadı",
    },
    "help": {
        "fa": "راهنمای ربات ناطق\n\nفرمان‌های موجود:\n/start - شروع ربات و نمایش منوی اصلی\n/help - نمایش این راهنما\n/random - دریافت یک آیه تصادفی\n/admin - ورود به بخش تنظیمات ادمین\n\nدکمه‌های منوی اصلی:\n- آیه تصادفی: ارسال یک آیه تصادفی\n- تنظیمات ادمین: بخش تنظیمات مدیریتی\n\nپس از دریافت آیه، اگر بستر پیام‌رسان از دکمه‌های درون‌خطی پشتیبانی کند، دکمه «آیه بعدی» نیز نمایش داده می‌شود.",
        "en": "Natiq Bot Help\n\nAvailable commands:\n/start - Start the bot and show the main menu\n/help - Show this help message\n/random - Receive a random ayah\n/admin - Open the admin settings area\n\nMain menu buttons:\n- Random Ayah: send a random ayah\n- Admin Settings: open the administrative settings area\n\nAfter receiving an ayah, the Next Ayah button will also appear when the messaging platform supports inline buttons.",
        "ar": "مساعدة بوت ناطق\n\nالأوامر المتاحة:\n/start - تشغيل البوت وإظهار القائمة الرئيسية\n/help - عرض هذه المساعدة\n/random - الحصول على آية عشوائية\n/admin - فتح قسم إعدادات المشرف\n\nأزرار القائمة الرئيسية:\n- آية عشوائية: إرسال آية عشوائية\n- إعدادات المشرف: فتح قسم الإعدادات الإدارية\n\nبعد استلام الآية، سيظهر زر الآية التالية أيضًا إذا كانت المنصة تدعم الأزرار المضمنة.",
        "tr": "Natiq Bot Yardım\n\nKullanılabilir komutlar:\n/start - Botu başlat ve ana menüyü göster\n/help - Bu yardım mesajını göster\n/random - Rastgele bir ayet al\n/admin - Yönetici ayarları alanını aç\n\nAna menü düğmeleri:\n- Rastgele Ayet: rastgele bir ayet gönderir\n- Yönetici Ayarları: yönetim ayarları alanını açar\n\nBir ayet aldıktan sonra, mesajlaşma platformu satır içi düğmeleri destekliyorsa Sonraki Ayet düğmesi de görünür.",
    },
    "admin_settings_placeholder": {
        "fa": "بخش تنظیمات ادمین فعال است، اما هنوز کامل نشده است. امکانات مدیریتی ربات در این بخش به‌صورت مرحله‌ای اضافه خواهند شد.",
        "en": "The admin settings area is available, but it is not complete yet. Administrative bot features will be added here incrementally.",
        "ar": "قسم إعدادات المشرف متاح، لكنه غير مكتمل بعد. ستتم إضافة ميزات إدارة البوت هنا بشكل تدريجي.",
        "tr": "Yönetici ayarları alanı kullanılabilir, ancak henüz tamamlanmamıştır. Bot yönetim özellikleri buraya aşamalı olarak eklenecektir.",
    },
    "admin_access_denied": {
        "fa": "شما به بخش ادمین دسترسی ندارید.",
        "en": "You do not have access to the admin area.",
        "ar": "ليس لديك صلاحية الوصول إلى قسم المشرف.",
        "tr": "Yönetici alanına erişim izniniz yok.",
    },
    "rate_limited": {
        "fa": "شما در مدت کوتاهی درخواست‌های زیادی فرستادید. لطفاً کمی صبر کنید و دوباره تلاش کنید.",
        "en": "You sent too many requests in a short time. Please wait a moment and try again.",
        "ar": "لقد أرسلت طلبات كثيرة خلال وقت قصير. يرجى الانتظار قليلًا ثم المحاولة مرة أخرى.",
        "tr": "Kısa sürede çok fazla istek gönderdiniz. Lütfen biraz bekleyip tekrar deneyin.",
    },
}


def normalize_language_code(value: str | None) -> str:
    if not value:
        return ""

    return value.strip().replace("_", "-").lower()


def _resolve_supported_language(value: str | None) -> SupportedLanguage | None:
    normalized = normalize_language_code(value)

    if not normalized:
        return None

    if normalized in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[normalized]

    primary = normalized.split("-", 1)[0]
    return LANGUAGE_ALIASES.get(primary)


def get_default_language() -> SupportedLanguage:
    settings = get_settings()
    resolved = _resolve_supported_language(settings.BOT_LANGUAGE)
    return resolved or "fa"


def detect_language(telegram_language_code: str | None) -> SupportedLanguage:
    resolved = _resolve_supported_language(telegram_language_code)

    if resolved:
        return resolved

    return get_default_language()


def get_message(
    key: str,
    language: SupportedLanguage,
) -> str:
    translations = MESSAGES[key]

    return str(translations.get(language) or translations[get_default_language()])
