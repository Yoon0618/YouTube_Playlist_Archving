import database_from_playlist
import database_from_spreadsheets

new_data = database_from_playlist.main()
spreadsheets_data = database_from_spreadsheets.main()

print(spreadsheets_data)

print(new_data)

# 새로 크롤링한 데이터에 스프레드시트 데이터 병합하기
v_number = 0
for v in spreadsheets_data:
    n_number = 0
    for n in new_data:
        if v[1] in n:
            new_data[n_number].insert(2, v[2])
            new_data[n_number].insert(3, v[3])
            new_data[n_number].insert(4, v[4])
            print(new_data)
        n_number += 1
    v_number += 1
