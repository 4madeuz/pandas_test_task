import pandas as pd

def count_category(accamulated_percent) -> str:
    '''Принимает pd.DataFrame, возвращает категорию в зависимости от накопленного процента'''
    if accamulated_percent['accumulated_percent_profit_product_of_warehouse'] <= 70:
        return 'A'
    elif accamulated_percent['accumulated_percent_profit_product_of_warehouse'] <= 90:
        return 'B'
    else:
        return 'C'

df = pd.read_json('data.json')
exploded_df = df.explode('products',ignore_index = True)

exploded_df = pd.concat([exploded_df.drop('products', axis = 1), 
pd.json_normalize(exploded_df['products'])], axis = 1)

#Задание 1 - стоимость тарифов доставки
exploded_df['highway_cost_total'] = exploded_df['highway_cost'] * exploded_df['quantity']
exploded_df['price_total'] = exploded_df['price'] * exploded_df['quantity']
print('Итоговые тарифы стоимости доставки для каждого склада:')
print(exploded_df.groupby('warehouse_name')['highway_cost_total'].sum())

#Задание 2 - отдельная таблица со статистикой товаров
products_total = exploded_df.groupby(
    'product', as_index=False).sum('quantity, highway_cost_total, price_total')
products_total.rename(
    columns = {'highway_cost_total':'expenses', 'price_total':'income'}, inplace = True)
products_total.drop(columns=['order_id','highway_cost','price'], axis= 1, inplace= True)
products_total['profit'] = products_total['income'] + products_total['expenses']
print('Статистика по товарам:')
print(products_total)

#Задание 3 - статистика по заказам и средняя прибыль
exploded_df['order_profit'] = exploded_df['price_total'] + exploded_df['highway_cost_total']
order_info = exploded_df.groupby('order_id', as_index=False)['order_profit'].sum()
print(f'Средняя прибыль всех заказов: {order_info["order_profit"].mean()}')
print(order_info)

#Задание 4 - Процент прибыли продукта в каждом конкретном складе
order_info = exploded_df.groupby(['warehouse_name', 'product',], as_index=False).sum('quantity, order_profit')
order_info.drop(columns=[
    'order_id','highway_cost','price', 'highway_cost_total', 'price_total'], axis= 1, inplace= True)
order_info['percent_profit_product_of_warehouse'] = order_info[
    'order_profit'] / order_info.groupby('warehouse_name')['order_profit'].transform('sum') *100
order_info = order_info.sort_values(by=[
    'warehouse_name', 'percent_profit_product_of_warehouse'], ascending=False)

#Задание 5 - Расчет накопленного процента
order_info['cum_sum'] = order_info.groupby('warehouse_name')['order_profit'].cumsum()
order_info['accumulated_percent_profit_product_of_warehouse'] = round(
    100*order_info.cum_sum/order_info.groupby('warehouse_name')['order_profit'].transform('sum'),2)

#Задание 6 - Присвоение категорий
order_info['category'] = order_info.apply(count_category, axis=1)

#Вывод результатов
print(order_info)
