Báo cáo phân tích vụ rẽ nhánh của MySQL và sự ra đời của MariaDB
1. Giới thiệu tổng quan
Trong hệ sinh thái phần mềm mã nguồn mở (FOSS), tính minh bạch và sự tin tưởng giữa đơn vị quản lý với cộng đồng là yếu tố sống còn. Khi mục tiêu thương mại của doanh nghiệp xung đột gay gắt với lợi ích chung của cộng đồng, rẽ nhánh (forking) trở thành cơ chế tự vệ tự nhiên. Vụ rẽ nhánh của quản trị cơ sở dữ liệu MySQL để tạo ra MariaDB vào năm 2009 là một trong những bài học kinh nghiệm điển hình nhất về mâu thuẫn quản trị và giấy phép trong lịch sử FOSS.

2. Nguyên nhân và diễn biến mâu thuẫn
MySQL vốn được phát triển bởi MySQL AB (Thụy Điển). Năm 2008, Sun Microsystems mua lại MySQL AB. Tuy nhiên, biến cố lớn thực sự xảy ra vào năm 2009 khi tập đoàn Oracle thông báo thâu tóm Sun Microsystems, qua đó nắm quyền sở hữu MySQL.

Sự kiện này đã dấy lên làn sóng lo ngại và phản đối dữ dội từ cộng đồng phát triển mã nguồn mở vì những lý do cốt lõi:

Xung đột lợi ích trực tiếp: Oracle vốn sở hữu cơ sở dữ liệu thương mại độc quyền hàng đầu thế giới (Oracle Database). Cộng đồng lo ngại Oracle sẽ cố tình "khai tử" hoặc làm suy yếu MySQL để tránh cạnh tranh với sản phẩm chủ lực của họ.

Mất niềm tin vào cách quản trị: Monty Widenius — nhà sáng lập chính của MySQL — nhận thấy Oracle thiếu sự cam kết với định hướng mã nguồn mở. Oracle dần khép kín quá trình phát triển, giảm tương tác với lập trình viên bên ngoài và chậm trễ trong việc sửa lỗi cộng đồng đóng góp.

Nguy cơ chuyển đổi giấy phép: Dù MySQL dùng giấy phép GNU GPL, quyền sở hữu trí tuệ tập trung trong tay Oracle khiến họ có thể thay đổi chính sách phân phối hoặc thương mại hóa các tính năng cao cấp (open-core model).

3. Quá trình rẽ nhánh và giải pháp từ MariaDB
Trước khi thương vụ thâu tóm hoàn tất, Monty Widenius đã tách khỏi dự án và thành lập MariaDB vào tháng 2 năm 2009. MariaDB được phát triển từ chính bản mã nguồn cuối cùng của MySQL tại thời điểm đó (phiên bản 5.1).

Để giải quyết triệt để các mâu thuẫn đã xảy ra với MySQL, dự án MariaDB áp dụng các chiến lược quản trị mới:

Thành lập MariaDB Foundation: Một tổ chức phi lợi nhuận độc lập được thành lập để nắm giữ thương hiệu và định hướng phát triển, đảm bảo không một tập đoàn đơn lẻ nào có thể thâu tóm dự án lần nữa.

Đảm bảo tính tương thích và cải tiến vượt trội: MariaDB duy trì khả năng thay thế trực tiếp (drop-in replacement) cho MySQL, giúp người dùng chuyển đổi mà không cần sửa đổi mã nguồn ứng dụng. Đồng thời, MariaDB tích hợp nhiều storage engine mới (như Aria, ColumnStore) và tối ưu hóa hiệu năng truy vấn tốt hơn.

Tăng cường tính rộng mở: Mọi tiến trình phát triển, báo lỗi và đóng góp mã nguồn đều được công khai hoàn toàn trên các nền tảng mã nguồn mở.

4. Tác động và bài học kinh nghiệm
Cuộc rẽ nhánh này đã làm thay đổi đáng kể cục diện thị trường cơ sở dữ liệu quan hệ:

Sự dịch chuyển của hệ sinh thái: Các hệ điều hành Linux lớn như Red Hat, CentOS, Debian và Arch Linux đã lần lượt gạt bỏ MySQL để chọn MariaDB làm cơ sở dữ liệu mặc định. Nhiều nền tảng và dịch vụ đám mây lớn cũng nhanh chóng tích hợp MariaDB.

Tạo động lực cạnh tranh: Sự bứt phá của MariaDB buộc Oracle không thể bỏ mặc MySQL. Oracle phải duy trì phiên bản MySQL Community và tích cực cải tiến (như bản MySQL 8.0) để duy trì thị phần.

Bài học rút ra:

Thành công của MariaDB chứng minh rằng sức mạnh cốt lõi của phần mềm mã nguồn mở không nằm ở tên thương hiệu hay tiềm lực tài chính của tập đoàn sở hữu, mà nằm ở sự đồng thuận của cộng đồng. Khi một doanh nghiệp thâu tóm mã nguồn mở nhưng cố tình áp đặt cơ chế quản trị khép kín, cộng đồng hoàn toàn có quyền và có đủ năng lực để tự tạo ra một bản phân nhánh mới tốt hơn để duy trì giá trị tự do ban đầu.
