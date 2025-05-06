# Отладочная плата PB_MCU01_H503

**PB_MCU01_H503** — это компактная и мощная отладочная плата на базе микроконтроллера **STM32H503CBT6** с ядром ARM Cortex-M33, разработанная российской компанией **ООО «Полярный Медведь – Электронные Технологии»**.

---

##  Основные характеристики

| Параметр                     | Значение                             |
|------------------------------|--------------------------------------|
| Микроконтроллер              | STM32H503CBT6                        |
| Ядро                         | ARM Cortex-M33                       |
| Частота                      | до 250 МГц                           |
| Flash-память                 | 128 КБ                               |
| RAM                          | 32 КБ                                |
| Питание                      | 3.3 В                                |
| Интерфейсы                   | USART, SPI, I2C, I3C, FDCAN, USB     |
| Таймеры                      | 16-битные таймеры общего назначения  |
| Входы/выходы                 | до 39 GPIO с альтернативными функциями |
| Тактовый генератор           | Встроенный HSI 64 МГц                |
| Отладка                      | Интерфейс SWD                        |
| Форм-фактор                  | Компактный DIP-модуль                |
| Рабочая температура          | -40...+85 °C                         |

---

##  Распиновка

- Полный доступ к выводам портов GPIO: PAx, PBx
- Отдельные пины для: SWDIO, SWCLK, NRST, VCC, GND
- Подходит для макетных плат (breadboard-friendly)

---

##  Производитель

**ООО «Полярный Медведь – Электронные Технологии**  
Официальный сайт: [https://pb-embedded.ru](https://pb-embedded.ru)

Плата изготавливается и поддерживается на территории Российской Федерации. Полностью совместима с программным обеспечением STM32Cube и другими инструментами STMicroelectronics.

---

##  Области применения

PB_MCU01_H503 используется в:

- Встраиваемых системах управления
- Разработке интерфейсных и сенсорных устройств
- Прототипировании промышленной и силовой электроники
- Образовании и обучении программированию STM32

---

##  Документация

- Руководство пользователя: по запросу (через нащ  официальный сайт: https://pb-embedded.ru/, либо на нашем яндекс диске: https://disk.yandex.ru/client/disk/TechnicalSupport )
- Сопровождается библиотеками STM32CubeH5 и поддерживается в STM32CubeIDE

# SPS-модуляция на STM32H503 (PB_MCU01_H503)

Этот проект демонстрирует реализацию SPS-модуляции (Single Phase Shift) на отладочной плате **PB_MCU01_H503**, разработанной компанией «Полярный Медведь». Плата построена на базе микроконтроллера STM32H503 (ядро Cortex-M33), с использованием таймера TIM1 в режиме complementary PWM с dead-time.

---

##  Ход настройки проекта

### 1. Конфигурация STM32CubeMX

- MCU: `STM32H503CBTx`
- Включены выводы:
  - `TIM1_CH1` → `PA8`
  - `TIM1_CH1N` → `PB13`
  - `TIM1_CH2` → `PA9`
  - `TIM1_CH2N` → `PB14`

- Таймер TIM1:
  - Prescaler = 63 (чтобы получить 1 МГц)
  - Counter Mode = Center-aligned
  - Period = 49 (чтобы получить 20 кГц)
  - Pulse = 25 (скважность 50%)
  - DeadTime = 5 (мертвое время между плечами)
  - Complementary output включены для CH1 и CH2

- Включена инициализация GPIO для соответствующих пинов

---

### 2. Генерация проекта

1. Открыт `.ioc` файл в STM32CubeMX
2. Настроены таймер и выводы
3. Генерация кода в STM32CubeIDE
4. Код вручную дополнен функцией фазового сдвига `Set_Phase_Shift()`

---

### 3. Прошивка

1. Плата PB_MCU01_H503 подключена через ST-Link v2 по интерфейсу SWD
2. Питание подано через USB
3. Прошивка выполняется через STM32CubeIDE (`Run → Debug` → `Resume`)

---

## 📄 Основной код настройки таймера (фрагмент из `main.c`)

```c
htim1.Instance = TIM1;
htim1.Init.Prescaler = 63;
htim1.Init.CounterMode = TIM_COUNTERMODE_CENTERALIGNED1;
htim1.Init.Period = 49;
htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
htim1.Init.RepetitionCounter = 0;
htim1.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
HAL_TIM_PWM_Init(&htim1);

TIM_OC_InitTypeDef sConfigOC = {0};
sConfigOC.OCMode = TIM_OCMODE_PWM1;
sConfigOC.Pulse = 25;
sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
sConfigOC.OCNPolarity = TIM_OCNPOLARITY_HIGH;
HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_1);
HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_2);

TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};
sBreakDeadTimeConfig.DeadTime = 5;
sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_ENABLE;
HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig);
```

---

##  Результат

На выходах `PA8` (CH1) и `PA9` (CH2) наблюдаются ШИМ-сигналы с частотой 20 кГц и заданным фазовым сдвигом. Dead-time корректно формируется между комплементарными сигналами CH1/CH1N и CH2/CH2N. Фазовый сдвиг между CH1 и CH2 устанавливается функцией:

```c
void Set_Phase_Shift(uint16_t shift_us)
{
  if (shift_us > 25) shift_us = 25;
  __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, 0);
  __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, shift_us);
}
```

---

##  Осциллограмма



---

## 📎 Полезные ссылки

- [PB_MCU01_H503 — документация (PDF)](docs/PB_MCU01_H503-UserManual.pdf)
- [ST-Link драйверы](https://www.st.com/en/development-tools/stsw-link009.html)
- [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html)
- [STM32CubeMX](https://www.st.com/en/development-tools/stm32cubemx.html)

---


