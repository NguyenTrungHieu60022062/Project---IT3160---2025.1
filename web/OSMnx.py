import osmnx as ox
import geopandas as gpd
import networkx as nx

# Địa điểm cần lấy dữ liệu
place_name = "Cau Giay, Hanoi, Vietnam"
output_filename = "caugiay_osmnx.geojson"

print(f"Bắt đầu lấy dữ liệu cho: {place_name}...")

# 1. Lấy đồ thị (graph) từ OSM
G = ox.graph_from_place(place_name, network_type='all')

G_components = list(nx.weakly_connected_components(G))
if len(G_components) > 1:
    print(f"Phát hiện {len(G_components)} 'đảo'. Đang giữ lại 'đảo' lớn nhất...")
    largest_comp = max(G_components, key=len)
    # Tạo đồ thị mới chỉ chứa "đảo" lớn nhất
    G = G.subgraph(largest_comp).copy()

print("Đã lấy dữ liệu đồ thị. Đang chuyển sang GeoDataFrame...")

# 2. Chuyển đồ thị sang GeoDataFrame
gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)

print("Đã chuyển đổi. Đang xử lý thuộc tính 'oneway'...")

# 3. Chuẩn hóa thuộc tính 'oneway'
if 'oneway' in gdf_edges.columns:
    gdf_edges['oneway'] = gdf_edges['oneway'].apply(lambda x: 'yes' if x is True else ('no' if x is False else x))
    print("Đã chuẩn hóa 'oneway' True/False sang 'yes'/'no'.")
else:
    print("Không tìm thấy cột 'oneway'. Bỏ qua.")


# 4. Lọc các cột cần thiết
columns_to_keep = [
    'geometry', 'osmid', 'name', 'highway', 
    'oneway', 'bridge', 'tunnel', 'layer', 'lanes'
]

final_columns = [col for col in columns_to_keep if col in gdf_edges.columns]
gdf_final_edges = gdf_edges[final_columns]

# In thông tin thống kê
print("-" * 30)
print("THỐNG KÊ DỮ LIỆU BÁO CÁO:")
print(f"1. Số lượng Nút (Nodes/States): {G.number_of_nodes()}")
print(f"2. Số lượng Cạnh (Edges/Actions): {G.number_of_edges()}")
print("-" * 30)

# 5. Lưu GeoDataFrame thành file GeoJSON
print(f"Đang lưu file vào: {output_filename}...")
gdf_final_edges.to_file(output_filename, driver="GeoJSON")

print("\n🎉 XONG!")
print(f"File '{output_filename}' đã được tạo. Hãy chép nó vào thư mục dự án của bạn.")