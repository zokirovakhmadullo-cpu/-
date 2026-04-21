@dp.message(F.text == "/stat")
async def show_top_20(message: types.Message):
    if not invites_count:
        await message.answer("📊 Ҳали ҳеч ким одам қўшмади.")
        return
        
    # Луғатни одам сони бўйича камайиш тартибида саралаймиз
    # x[1] - бу қўшилган одамлар сони
    sorted_stats = sorted(invites_count.items(), key=lambda x: x[1], reverse=True)
    
    # Фақат биринчи 20 тасини оламиз
    top_20 = sorted_stats[:20]
    
    text = "🏆 **Энг кўп одам қўшганлар ТОП-20:**\n\n"
    
    for index, (user_id, count) in enumerate(top_20, start=1):
        # Фойдаланувчи исмини олишга ҳаракат қиламиз
        try:
            member = await bot.get_chat_member(message.chat.id, user_id)
            name = member.user.full_name
        except:
            name = f"ID: {user_id}" # Агар исмини ололмаса ID ни чиқаради
            
        text += f"{index}. 👤 {name} — **{count}** та аъзо\n"
    
    await message.answer(text, parse_mode="Markdown")
