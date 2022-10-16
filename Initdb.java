import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.ResultSet;
import java.sql.Statement;
import java.sql.PreparedStatement;
import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;
import java.util.stream.Stream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.io.IOException;

public class Initdb {

	private static Connection connect(String url) {
		Connection conn = null;
		try {
			conn = DriverManager.getConnection(url);
		} catch (SQLException e) {
			System.out.println(e.getMessage());
        }
		return conn;
	}
			   

    public static void main(String[] args) {
		String url = args[0];;
		write(url);
	}

	public static void write(String url) {
		Connection conn=null;
		try {
			conn = connect(url);
            File file = new File("database.txt");
            Scanner sn = new Scanner(file);
			String sql = """
			 	pragma journal_mode = WAL;
				pragma synchronous = normal;
			""";
 			Statement stmt  = conn.createStatement();
			stmt.executeUpdate(sql);

			String insertSQL = "INSERT INTO urlMap (short, long) VALUES (?, ?)";
			PreparedStatement ps = conn.prepareStatement(insertSQL);
			int count = 0;
			Path filePath = Paths.get("database.txt");
			Stream<String> lines = Files.lines( filePath );
            while(sn.hasNextLine()) {
                String line = sn.nextLine();
				String[] tmp = line.split("\t", 2);
				String shortURL = tmp[0];
				String longURL = tmp[1];
				ps.setString(1, shortURL);
				ps.setString(2, longURL);
				ps.execute();
				count++;
				if(count % 1000 == 0) {System.out.println(count);}
            }
			System.out.println(count + " lines inserted");
			// lines.forEach((line) -> {
			// 	String[] tmp = line.split("\t", 2);
			// 	try {
			// 		ps.setString(1, tmp[0]);
			// 		ps.setString(2, tmp[1]);
			// 		ps.execute();
			// 		count++;
			// 		if(count % 1000 == 0) {System.out.println(count);}
			// 	} catch (SQLException e) {
			// 		System.out.println(e.getMessage());
			// 	} 
			// });

		} catch (SQLException e) {
			System.out.println(e.getMessage());
		} catch (FileNotFoundException e) {
            System.out.println(e.getMessage());
        } catch (IOException e) {
            System.out.println(e.getMessage());
		}
        finally {
            try {
                if (conn != null) {
                    conn.close();
                }
            } catch (SQLException ex) {
                System.out.println(ex.getMessage());
            }
		}
	}
	public static void read(String url) {
		Connection conn=null;
		try {
			conn = connect(url);
			Statement stmt  = conn.createStatement();
			String sql = "SELECT leftside, rightside FROM stuff";
			ResultSet rs = stmt.executeQuery(sql);
			int count = 0;
			while (rs.next()) {
				count ++;
				// System.out.println( rs.getString("leftside") + "\t" + rs.getInt("rightside") );
			}
			System.out.println(count);
		} catch (SQLException e) {
			System.out.println(e.getMessage());
        	} finally {
            		try {
                		if (conn != null) {
                    			conn.close();
                		}
            		} catch (SQLException ex) {
                		System.out.println(ex.getMessage());
            		}
		}
	}
}
