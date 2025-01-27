from aiogram import Router, F
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from utils.file_processing import remove_video_metadata, add_gaussian_noise_to_video
from utils.helpers import generate_random_filename, calculate_md5
from sqlalchemy.orm import Session
from database import SessionLocal, get_or_create_user, increment_usage
import os

router = Router()

MAX_FREE_REQUESTS = 5  # Максимальное количество бесплатных запросов

@router.message(F.video)
async def handle_video(message: Message):
    db: Session = SessionLocal()  # Подключение к базе данных
    user = get_or_create_user(db, message.from_user.id)

    # Вычисляем оставшееся количество бесплатных попыток
    remaining_requests = MAX_FREE_REQUESTS - user.usage_count

    # Проверяем лимит бесплатных запросов
    if remaining_requests <= 0 and not user.is_paid:
        # Создаем клавиатуру с кнопкой "Оплатить"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Оплатить",
                        url="https://www.google.com/"  # Укажите вашу ссылку для оплаты
                    )
                ]
            ]
        )

        # Сообщение о превышении лимита с кнопкой
        await message.answer(
            "😢 Закончились бесплатные уникализации, оплатите подписку всего за 99 рублей - для приобретения доступа на месяц. Продление автоматическое.",
            reply_markup=keyboard
        )
        return

    video = message.video
    file_path = f"{video.file_id}.mp4"
    output_path_cleaned = generate_random_filename("mp4")
    output_path_noisy = generate_random_filename("mp4")

    # Получаем объект файла и скачиваем видео
    file = await message.bot.get_file(video.file_id)
    await message.bot.download_file(file.file_path, file_path)
    await message.answer("👀 Началась обработка видео")

    try:
        # Удаление метаданных
        remove_video_metadata(file_path, output_path_cleaned)

        # Добавление шума
        add_gaussian_noise_to_video(output_path_cleaned, output_path_noisy, noise_level=0.01)

        # Увеличиваем использование
        increment_usage(db, message.from_user.id)
        remaining_requests -= 1  # Уменьшаем оставшиеся запросы

        # Вычисление хэш-сумм
        original_hash = calculate_md5(file_path)
        noisy_hash = calculate_md5(output_path_noisy)

        # Отправляем результат
        file_to_send = FSInputFile(output_path_noisy)
        await message.answer_document(file_to_send, caption="✅ Готово")
        await message.answer(
            f"🎉 Осталось бесплатных уникализаций: {remaining_requests}/{MAX_FREE_REQUESTS}\n"
            f"Хэш-суммы файлов:\nОригинал: {original_hash}\nС шумом: {noisy_hash}"
        )
    finally:
        db.close()  # Закрываем сессию базы данных
        # Удаляем временные файлы
        for path in [file_path, output_path_cleaned, output_path_noisy]:
            if os.path.exists(path):
                os.remove(path)
