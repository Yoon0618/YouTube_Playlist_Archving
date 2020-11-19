new_data = [["A","가"],["B","나"],["D","라"],["C","다"]]
spreadsheets_data = [["A","가","1", "YT1", "game1"],["B","나","2", "YT2", ""],["C","다","3" , "", "game4"]]

# import database_from_playlist
# import database_from_spreadsheets

# 새로 크롤링한 데이터에 스프레드시트 데이터 병합하기
v_number = 0
for v in spreadsheets_data:
    n_number = 0
    for n in new_data:
        if v[0] in n:
            new_data[n_number].insert(2, v[2])
            new_data[n_number].insert(3, v[3])
            new_data[n_number].insert(4, v[4])
            print(new_data)
            
        n_number += 1
    v_number += 1
