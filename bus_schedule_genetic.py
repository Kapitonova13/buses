import math
import random
#######################################################################################################
# Основнвые переменные
route = 60 # время всего маршрута (1 ч)
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
        self.last_time = None # время послежнего рейса

    def empty_bus(self, current_driver, current_time):
        if self.is_occupied == False: # проверка на занятость автобуса
            # print(f"Автобус {self.bus_number} занят водителем {current_driver.driver_id} в {format_time(current_time)}")
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
        if self.total_work_minutes >= self.max_work_minutes:
            # print(f"Водитель {self.driver_id} закончил работу в {format_time(current_time)}. Автобус {bus.bus_number} свободен")
            self.total_work_minutes = 0
            bus.is_occupied = False         # Сбрасываем состояние автобуса и водителя в начале каждого дня
            bus.current_driver = None
            return True

    def remaining_time(self, bus):
        remaining_time_minutes = self.max_work_minutes - self.total_work_minutes
        # print(f"Автобус {bus.bus_number}, Водитель {self.driver_id}: отработано {format_time(self.total_work_minutes)}, осталось {format_time(remaining_time_minutes)}")

class Driver8(Driver):
    def __init__(self, driver_id):
        super().__init__(driver_id, max_work_minutes=8 * 60, lunch_break_minutes=60)
        self.lunch = [12, 13, 14] # обеденный перерыв

    def lunch_break(self, current_time, bus):
        time_str = format_time(current_time)
        hour = int(time_str.split(':')[0])
        # print(hour)
        if (hour >= self.lunch[0] and hour < self.lunch[1] and self.driver_id % 2 != 0) or ( hour >= self.lunch[1] and hour < self.lunch[2] and self.driver_id % 2 == 0):  # Проверяем часы
            # print(f"Автобус {bus.bus_number}, Водитель {self.driver_id}: ушел на обед с {format_time(current_time)} до {format_time(current_time + self.lunch_break_minutes)}")
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
    return current_time

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
            # print(f"Водитель {current_driver.driver_id} делает перерыв в {format_time(current_time - current_driver.lunch_break_minutes)} на {current_driver.lunch_break_minutes} минут.")
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
    return current_time

#######################################################################################################

# генерируется расписание движения автобусов
def bus_schedule(num_buses, initial_time_minutes, interval_minutes, stop_interval_minutes, bus_stops):
    buses = [Bus(i+1) for i in range(num_buses)]
    drivers = []
    drivers12 = []
    driver_count = 0
    driver_count12 = 0
    num_drivers_per_group = len(buses) 
    num_groups = 3         
    working_day = initial_time_minutes
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

    for i in range(len(buses)): 
        driver_count += 1
        drivers.append(Driver8(driver_count))

    for group_num in range(num_groups):
            for i in range(num_drivers_per_group):
                driver_count12 += 1
                drivers12.append(Driver12(driver_count12))
    
    time_str = format_time(initial_time_minutes)
    hour = int(time_str.split(':')[0])
    
    if 6 <= hour < 10:  
        for bus in buses: # 8-часовые
                departure_time = initial_time_minutes + (bus.bus_number - 1) * interval_minutes 
                process_bus_for8(bus, drivers, stop_interval_minutes, departure_time)
        for driver in drivers[:1]:
            first_times = [trip_schedule[0] for trip_schedule in driver.schedule if trip_schedule] # проверка на пустоту
            first_eight_times = first_times[:8] 
            last_time_str = first_eight_times[-1]
            hours, minutes = map(int, last_time_str.split(':'))
            new_hour = hours + 1
            new_time_str = "{:02d}:{:02d}".format(new_hour, minutes)
            first_eight_times.append(new_time_str)
            return first_eight_times

    else:
        for bus in buses:
            departure_time = initial_time_minutes + (bus.bus_number - 1) * interval_minutes
            process_bus(bus, drivers12, 0, num_drivers_per_group, stop_interval_minutes, departure_time)
        for driver in drivers12[:1]:
            first_times = [trip_schedule[0] for trip_schedule in driver.schedule if trip_schedule] # проверка на пустоту
            first_eight_times = first_times[:12] 
            last_time_str = first_eight_times[-1]
            hours, minutes = map(int, last_time_str.split(':'))
            new_hour = hours + 1
            new_time_str = "{:02d}:{:02d}".format(new_hour, minutes)
            first_eight_times.append(new_time_str)        
            # print(f"12-часовой водитель {driver.driver_id} на стоянке : {first_eight_times}")
            return first_eight_times


#######################################################################################################
# переменные для генетического алгоритма

lenght = 16 # длина одного индивада
size_population = 10 # кол-во индивидуумов в популяции
cross = 0.9 # вер-ть скрещивания
mutation = 0.1 # вер-ть мутации
max_generation = 40 # макс-ое кол-во поколений

#######################################################################################################

def generate_time_array(begin_day1, lenght):
    begin_day = random.randint(begin_day1, begin_day1+2*60)
    end_day = begin_day + 12*60 
    times = [begin_day]  # добавляем begin_day как первый элемент
    # генерируем остальные случайные времена
    while len(times) < lenght:
        new_time = random.randint(begin_day, end_day)
        if new_time not in times: # проверка на дубликаты
            times.append(new_time)
    times.sort()
    return [format_time(time_minutes) for time_minutes in times]

def generates_start_time():
    shed = generate_time_array(initial_time_minutes, lenght) 
    mass = []
    for i in shed:
        hours, minutes = map(int, i.split(':'))
        new_time = hours * 60 + minutes 
        m = bus_schedule(buses, new_time, rounded_interval, time_between_stops, bus_stops) 
        mass.append(m)
    return mass

class FitnessMax():
    def __init__(self):
        self.values = [0] # начальная приспособленность особи - 0

class Individual(list): # класс наследуется от базового list 
    def __init__(self, *args):
        super().__init__(*args)
        self.fitness = FitnessMax() #вычисление приспособленности

def Fitness(individual):
    fitness = 0
    for shed in individual:
        for time in shed: 
            hours, minutes = map(int, time.split(':'))
            new_time = hours * 60 + minutes 
            if (6 * 60 <= new_time < 9 * 60) or (17 * 60 + 30 <= new_time < 20 * 60 + 30): #время час пик
                fitness += 1
    return fitness

def individCreator(): 
    time_array = generates_start_time()
    return Individual(time_array)

def populationCreator(n):  # создает популяцию
    return [individCreator() for _ in range(n)]

population = populationCreator(n = size_population)
generation_k = 0 #подсчет поколений

fitnessValues = list(map(Fitness, population)) # список из приспособленностей особой текущей популяции( вызовем для каждого инд-ма ф-ю приспособленности)

for individual, fitnessValue in zip(population, fitnessValues): # обновляются значения приспособленности для каждой особи в популяции
    individual.fitness.values = fitnessValue

def clone(value): #клонирование отдельного инд-ма
    ind = Individual(value[:])
    ind.fitness.values = value.fitness.values
    return ind

def otbTourn(population, p_len): #турнирный отбор
    new_popul = [] #новый список из отобранных особей
    for n in range(p_len):
        i1 = i2 = i3 = 0
        while i1 == i2 or i1 == i3 or i2 == i3: # случ образом отбираем 3х особей, чтобы индексы были различными
            i1, i2, i3 = random.randint(0, p_len - 1), random.randint(0, p_len - 1), random.randint(0, p_len - 1)  
        new_popul.append(max([population[i1], population[i2], population[i3]], key=lambda ind: ind.fitness.values)) #из этих особей отбираем ту, у которой макс приспособленность
    return new_popul

def crosOnePoint(ch1, ch2): # передаем 2х родителей и на их основе формируем 2х потомков
    s = random.randint(2, len(ch1) - 3) # точка разреза(случ образом, но чтобы границы не попадали)
    ch1[s:], ch2[s:] = ch2[s:], ch1[s:]

def mutation_time(mut, indpb=mutation):  # indpb - вер-ть мутации отдельного гена
    if random.random() < mutation:
        i1, i2 = random.sample(range(len(mut)), 2)
        mut[i1], mut[i2] = mut[i2], mut[i1]  # меняем местами два случайных элемента


fitnessValues = [individual.fitness.values for individual in population] #коллекция из значений приспос-ей особей в данной популяции


best_overall_individual = None
best_overall_fitness = 0

while generation_k < max_generation:
    generation_k += 1
    new = otbTourn(population, len(population)) # отбираем лучших особей
    new = list(map(clone, new)) # клонируем их, чтобы не было повторений

    for ch1, ch2 in zip(new[::2], new[1::2]): # скрещивание (четный эл-т и нечет - неповтор. пары)
        if random.random() < cross: # с такой вер-тью формируем 2х потомков 
            crosOnePoint(ch1, ch2)
    
    for mut in new: # мутации
        if random.random() < mutation:
            mutation_time(mut, indpb=1.0/lenght)

    freshFitnessValues = list(map(Fitness, new)) #обновляем значения приспос-ей новой популяции
    for individual, fitnessValue in zip(new, freshFitnessValues):
        individual.fitness.values = fitnessValue

    population[:] = new # обновляем популяцию 

    fitnessValues = [ind.fitness.values for ind in population] #обновляем значения приспос-ей особей в популяции

    best_ind = fitnessValues.index(max(fitnessValues))
    current_best_fitness = max(fitnessValues)
    if current_best_fitness > best_overall_fitness:
        best_overall_fitness = current_best_fitness
        best_overall_individual = population[best_ind]


print(f"\nЛучший индивидуум")
n8 = 1
n12 = 1
bestind = population[best_ind]
bestind.sort()
for i in population[best_ind]:
    if len(i) < 10:
        print(f"8-часовой водитель {n8} на стоянке : {i}")
        n8 += 1
    else:
        print(f"12-часовой водитель {n12} на стоянке : {i}")
        n12 += 1

