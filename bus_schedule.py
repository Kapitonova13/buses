import math
#######################################################################################################
# Основнвые переменные
route = 60 # время всего маршрута в минутах
buses = 8 # 8 автобусов 
bus_stops = 6 # кол-во автобусных остановок(включая стоянку)
time_between_stops = route//bus_stops # время между остановками
interval_between_buses = route/buses # интервал между остановками
rounded_interval = math.ceil(interval_between_buses)
initial_time_minutes = 60*6 # начало рабочего дня

#######################################################################################################

class Bus:
    def __init__(self, bus_number):
        self.bus_number = bus_number # номер автобуса
        self.is_occupied = False  # автобус свободен\занят
        self.current_driver = None # текущий водитель автобуса

    def empty_bus(self, current_driver, current_time):
        if self.is_occupied == False: # проверка на занятость автобуса
                    print(f"Автобус {self.bus_number} занят водителем {current_driver.driver_id} в {format_time(current_time)}")
                    self.is_occupied = True # занят
                    self.current_driver = current_driver # запоминаем текущего водителя

class Driver:
    def __init__(self, driver_id, max_work_minutes, lunch_break_minutes):
        self.driver_id = driver_id # идентификатор водителя 
        self.lunch_break_minutes = lunch_break_minutes # длительность обеденного перерыва 
        self.schedule = [] # расписание водителя 
        self.total_work_minutes = 0 # общее время работы водителя 
        self.max_work_minutes = max_work_minutes # максимальное время работы водителя 

    def add_trip(self, trip_schedule,current_time, bus, departure_time):
        self.schedule.append(trip_schedule)
        self.total_work_minutes += calculate_trip_duration(trip_schedule)
        # print(self.total_work_minutes, self.max_work_minutes)
        if self.total_work_minutes >= self.max_work_minutes:
            print(f"Водитель {self.driver_id} закончил работу в {format_time(current_time)}. Автобус {bus.bus_number} свободен")
            self.total_work_minutes = 0
            bus.is_occupied = False         # сбрасываем состояние автобуса и водителя в начале каждого дня
            bus.current_driver = None
            return True

    def remaining_time(self, bus):
        remaining_time_minutes = self.max_work_minutes - self.total_work_minutes
        print(f"Автобус {bus.bus_number}, Водитель {self.driver_id}: отработано {format_time(self.total_work_minutes)}, осталось {format_time(remaining_time_minutes)}")
      

class Driver8(Driver):
    def __init__(self, driver_id):
        super().__init__(driver_id, max_work_minutes=8 * 60, lunch_break_minutes=60)
        self.lunch = [12, 13, 14] # обеденный перерыв

    def lunch_break(self, current_time, bus):
        time_str = format_time(current_time)
        hour = int(time_str.split(':')[0])
        # print(hour)
        if (hour >= self.lunch[0] and hour < self.lunch[1] and self.driver_id % 2 != 0) or ( hour >= self.lunch[1] and hour < self.lunch[2] and self.driver_id % 2 == 0):  # Проверяем часы
            print(f"Автобус {bus.bus_number}, Водитель {self.driver_id}: ушел на обед с {format_time(current_time)} до {format_time(current_time + self.lunch_break_minutes)}")
            return True

class Driver12(Driver):
    def __init__(self, driver_id):
        super().__init__(driver_id, max_work_minutes=12 * 60, lunch_break_minutes=10)


#######################################################################################################
#общие ф-ии

# форматирует общее количество минут в формат ЧЧ:ММ, учитывая цикличность  
def format_time(total_minutes):
    hours = (total_minutes // 60) % 24  # остаток от деления на 24
    minutes = total_minutes % 60
    return "{:02d}:{:02d}".format(hours, minutes)

# вычисляет продолжительность поездки (в минутах), учитывая переход через полночь
def calculate_trip_duration(trip_schedule):
    departure_time_minutes = int(trip_schedule[0].split(':')[0]) * 60 + int(trip_schedule[0].split(':')[1])
    arrival_time_minutes = int(trip_schedule[-1].split(':')[0]) * 60 + int(trip_schedule[-1].split(':')[1])

    duration = arrival_time_minutes - departure_time_minutes
    # для перехода через полночь
    if duration < 0:
        duration += 24 * 60  # добавляем 24 часа (в минутах), если duration отрицательное
    return duration

def drivers12_choice(bus, group_index, num_drivers_per_group, drivers12):
        # выбираем водителя из текущей группы
        driver_index = bus.bus_number - 1 #  0-7
        driver_id_offset = group_index * num_drivers_per_group
        current_driver = drivers12[driver_index + driver_id_offset] 
        return current_driver

def process_bus_for8(bus, drivers, stop_interval_minutes, departure_time):
    on = True
    while on:
        current_time = departure_time
        current_driver = drivers[bus.bus_number - 1]
        bus.empty_bus(current_driver, current_time)
        if current_driver.lunch_break(current_time, bus):
            departure_time += current_driver.lunch_break_minutes # добавляем час на обед
            continue  # переходим к следующему рейсу                
        trip_schedule = [format_time(current_time)]
        for stop_num in range(1, bus_stops): #время остановок
            current_time += stop_interval_minutes
            trip_schedule.append(format_time(current_time))
        current_time += stop_interval_minutes
        trip_schedule.append(format_time(current_time))
        departure_time = current_time
        # current_driver.remaining_time(bus)
        if current_driver.add_trip(trip_schedule,current_time, bus, departure_time):
            on = False

def process_bus(bus, drivers12, group_index, num_drivers_per_group, stop_interval_minutes, departure_time):
    on = True
    for_lunch = departure_time
    while on:
        current_time = departure_time
        # выбираем водителя из текущей группы
        current_driver = drivers12_choice(bus, group_index, num_drivers_per_group, drivers12) 
        bus.empty_bus(current_driver, current_time)
        if current_time - for_lunch >= 3 * 60:  # каждые 3 часа перерыв
            for_lunch = current_time
            current_time += current_driver.lunch_break_minutes  
            print(f"Водитель {current_driver.driver_id} делает перерыв в {format_time(current_time - current_driver.lunch_break_minutes)} на {current_driver.lunch_break_minutes} минут.")
        trip_schedule = [format_time(current_time)]
        for stop_num in range(1, bus_stops): #время остановок
            current_time += stop_interval_minutes
            trip_schedule.append(format_time(current_time))
        current_time += stop_interval_minutes
        trip_schedule.append(format_time(current_time))
        departure_time = current_time
        # current_driver.remaining_time(bus)
        if current_driver.add_trip(trip_schedule,current_time, bus, departure_time):
            on = False


#######################################################################################################

# генерируется расписание движения автобусов
def bus_schedule(num_buses=buses, initial_time_minutes=initial_time_minutes, interval_minutes=rounded_interval, stop_interval_minutes=time_between_stops, bus_stops=bus_stops):
    buses = [Bus(i+1) for i in range(num_buses)]
    drivers = []
    drivers12 = []
    driver_count = 0
    driver_count12 = 0
    num_drivers_per_group = len(buses) 
    num_groups = 3         
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

    for i in range(len(buses)): 
        driver_count += 1
        drivers.append(Driver8(driver_count))

    for group_num in range(num_groups):
            for i in range(num_drivers_per_group):
                driver_count12 += 1
                drivers12.append(Driver12(driver_count12))

    for day_index, day in enumerate(days):
        print(f"\n--- {day} ---")
        group_index = day_index % num_groups # 0, 1, 2, 0, 1, 2, 0...
        time_str = format_time(initial_time_minutes)
        hour = int(time_str.split(':')[0])
        if 6 <= hour < 10:  # Время для 8-часовых водителей
            if day in ["Суббота", "Воскресенье"]:
                for bus in buses:
                    if bus.bus_number % 2 != 0:
                        departure_time = initial_time_minutes + (bus.bus_number - 1) * interval_minutes #отсчет с начала рабочего дня
                        process_bus(bus, drivers12, group_index, num_drivers_per_group, stop_interval_minutes, departure_time)
                    else:
                        departure_time = initial_time_minutes + (bus.bus_number - 1) * interval_minutes + 12*60 
                        process_bus(bus, drivers12, group_index, num_drivers_per_group, stop_interval_minutes, departure_time)

            else:
                for bus in buses: # 8-часовые
                        departure_time = initial_time_minutes + (bus.bus_number - 1) * interval_minutes 
                        process_bus_for8(bus, drivers, stop_interval_minutes, departure_time)
                print(f"\nСмена 12-часовых")
                for bus in buses: 
                    if bus.bus_number % 2 != 0:
                        departure_time = initial_time_minutes + 9*60 + 10 + (bus.bus_number - 1) * interval_minutes
                        process_bus(bus, drivers12, group_index, num_drivers_per_group, stop_interval_minutes, departure_time)
                    else: 
                        departure_time = 17*60 + 10 + (bus.bus_number - 1) * interval_minutes
                        process_bus(bus, drivers12, group_index, num_drivers_per_group, stop_interval_minutes, departure_time)
        else:
            print("Рабочий день может начинаться с 6:00 - 10:00 (в 6:00, 7:00, 8:00, 9:00)")
            return
  


    all_drivers = len(drivers) + len(drivers12)
    all_drivers2 = len(drivers) + (len(drivers12)//3)
    print()
    print(f"Общее количество водителей в сутки: {all_drivers2}")
    print(f"Общее количество водителей в неделю: {all_drivers}") 

    # вывод расписания для каждого водителя
    for driver in drivers:
        # print(f"\nРасписание для {driver.driver_id}-го водителя:")
        # for trip_schedule in driver.schedule:
        #     print(trip_schedule)

        first_times = [trip_schedule[0] for trip_schedule in driver.schedule if trip_schedule] # проверка на пустоту
        first_eight_times = first_times[:8] 
        last_time_str = first_eight_times[-1]
        hours, minutes = map(int, last_time_str.split(':'))
        new_hour = hours + 1
        new_time_str = "{:02d}:{:02d}".format(new_hour, minutes)
        first_eight_times.append(new_time_str)
        print(f"8-часовой водитель {driver.driver_id} на стоянке : {first_eight_times}")


    # for driver in drivers12:
    #     print(f"\nРасписание для {driver.driver_id}-го водителя:")
    #     for trip_schedule in driver.schedule:
    #         print(trip_schedule)
    for driver in drivers12:
        first_times = [trip_schedule[0] for trip_schedule in driver.schedule if trip_schedule] # проверка на пустоту
        first_eight_times = first_times[:12] 
        last_time_str = first_eight_times[-1]
        hours, minutes = map(int, last_time_str.split(':'))
        new_hour = hours + 1
        new_time_str = "{:02d}:{:02d}".format(new_hour, minutes)
        first_eight_times.append(new_time_str)
        print(f"12-часовой водитель {driver.driver_id} на стоянке : {first_eight_times}")

    print()
    print("Расписание на выходной(вс):")
    for driver in drivers12[:8]:
        first_times = [trip_schedule[0] for trip_schedule in driver.schedule if trip_schedule] # проверка на пустоту
        first_eight_times = first_times[-12:] 
        print(f"12-часовой водитель {driver.driver_id} на стоянке : {first_eight_times}")

    def print_schedule():
        print("-"*100)
        print("Неделя № 1")
        print("Пн, Чт, Вс: 1 смена 12-часовых водителей")
        print("Вт, Пт: 2 смена 12-часовых водителей")
        print("Ср, Сб: 3 смена 12-часовых водителей")
        print("Неделя № 2")
        print("Пн, Чт, Вс: 2 смена 12-часовых водителей")
        print("Вт, Пт: 3 смена 12-часовых водителей")
        print("Ср, Сб: 1 смена 12-часовых водителей")
        print("Неделя № 3")
        print("Пн, Чт, Вс: 3 смена 12-часовых водителей")
        print("Вт, Пт: 1 смена 12-часовых водителей")
        print("Ср, Сб: 2 смена 12-часовых водителей")
        print("и т. д.")
    print_schedule()

if __name__ == "__main__":
    bus_schedule()


