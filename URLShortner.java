import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.PrintWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.URL;
import java.net.URLDecoder;
import java.util.Date;
import java.util.StringTokenizer;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.ResultSet;
import java.sql.Statement;
import java.sql.PreparedStatement;
import java.util.*;

public class URLShortner { 
	
	static final File WEB_ROOT = new File(".");
	static final String DEFAULT_FILE = "index.html";
	static final String FILE_NOT_FOUND = "404.html";
	static final String METHOD_NOT_SUPPORTED = "not_supported.html";
	static final String REDIRECT_RECORDED = "redirect_recorded.html";
	static final String REDIRECT = "redirect.html";
	static final String NOT_FOUND = "notfound.html";
	static final String DATABASE = "database.txt";
	static final String SQLITE = "/virtual/dongshu4/URLShortner/urlMap.db";

	// port to listen connection
	static final int PORT = 8851;


	static HashMap<String, String> entries = new HashMap<String, String>();

	public static void main(String[] args) {
		loadMap();


		try {
			File file = new File(WEB_ROOT, FILE_NOT_FOUND);
			int not_found_file_length = (int) file.length();
			byte[] not_found_file_data = readFileData(file, not_found_file_length);

			
			ServerSocket serverConnect = new ServerSocket(PORT);
			System.out.println("Server started.\nListening for connections on port : " + PORT + " ...\n");
						
			// we listen until user halts server execution
			while (true) {
				// handle(serverConnect.accept());
				HTTPWorker clientSock = new HTTPWorker(serverConnect.accept(), entries, not_found_file_length, not_found_file_data);
				new Thread(clientSock).start();
			}
		} catch (IOException e) {
			System.err.println("Server Connection error : " + e.getMessage());
		}
	}

	public static void loadMap() {
		Connection conn=null;
		try {
			conn = DriverManager.getConnection("jdbc:sqlite:" + SQLITE);
			String sql = "SELECT short, long FROM urlMap";
			PreparedStatement ps  = conn.prepareStatement(sql);

			ResultSet rs = ps.executeQuery();
			while(rs.next()) {
				entries.put(rs.getString("short"), rs.getString("long"));
			}

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


	private static byte[] readFileData(File file, int fileLength) throws IOException {
		FileInputStream fileIn = null;
		byte[] fileData = new byte[fileLength];
		
		try {
			fileIn = new FileInputStream(file);
			fileIn.read(fileData);
		} finally {
			if (fileIn != null) 
				fileIn.close();
		}
		
		return fileData;
	}


}


class HTTPWorker implements Runnable {
	static final File WEB_ROOT = new File(".");
	static final String DEFAULT_FILE = "index.html";
	static final String FILE_NOT_FOUND = "404.html";
	static final String METHOD_NOT_SUPPORTED = "not_supported.html";
	static final String REDIRECT_RECORDED = "redirect_recorded.html";
	static final String REDIRECT = "redirect.html";
	static final String NOT_FOUND = "notfound.html";
	static final String DATABASE = "database.txt";
	static final String SQLITE = "/virtual/dongshu4/URLShortner/urlMap.db";

	private final Socket connect;
	private Map<String, String> entries;


	private byte[] not_found_file_data;
	int not_found_file_length;
	public HTTPWorker(Socket socket, Map<String, String> entries, int not_found_file_length, byte[] not_found_file_data) {
		this.connect = socket;
		this.entries = entries;
		this.not_found_file_data = not_found_file_data;
		this.not_found_file_length = not_found_file_length;

	}



	public void run() {
		BufferedReader in = null; PrintWriter out = null; BufferedOutputStream dataOut = null;
		
		try {
			in = new BufferedReader(new InputStreamReader(connect.getInputStream()));
			out = new PrintWriter(connect.getOutputStream());
			dataOut = new BufferedOutputStream(connect.getOutputStream());
			
			String input = in.readLine();

			Pattern pput = Pattern.compile("^PUT\\s+/\\?short=(\\S+)&long=(\\S+)\\s+(\\S+)$");
			Matcher mput = pput.matcher(input);
			if(mput.matches()){
				String shortResource=mput.group(1);
				String longResource=mput.group(2);
				String httpVersion=mput.group(3);
				entries.put(shortResource, longResource);

				// saveDB(shortResource, longResource);
				// save(shortResource, longResource);

				File file = new File(WEB_ROOT, REDIRECT_RECORDED);
				int fileLength = (int) file.length();
				String contentMimeType = "text/html";
				//read content to return to client
				byte[] fileData = readFileData(file, fileLength);
					
				out.println("HTTP/1.1 200 OK");
				out.println("Server: Java HTTP Server/Shortner : 1.0");
				out.println("Date: " + new Date());
				out.println("Content-type: " + contentMimeType);
				out.println("Content-length: " + fileLength);
				out.println(); 
				out.flush(); 

				dataOut.write(fileData, 0, fileLength);
				dataOut.flush();
			} else {
				String decodedUrl = URLDecoder.decode(input, StandardCharsets.UTF_8.toString());
				Pattern pconvert= Pattern.compile("^GET\\s+/\\?(\\S+)=(\\S+)\\s+(\\S+)$");
				Matcher mconvert = pconvert.matcher(decodedUrl);
				if(mconvert.matches()) {
					String mode=mconvert.group(1);
					String data=mconvert.group(2);
					String httpVersion=mconvert.group(3);
					String result=null;
					if(mode.equals("stl")) {
						result = entries.get(data);
						// result=findDB(data);
					} else if (mode.equals("lts")) {
						// result=findDBShort(data);
						//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
					}

					if(result!=null){
						byte[] resultByte = result.getBytes();
						int fileLength = (int) resultByte.length;
						String content = "text/html";
						out.println("HTTP/1.1 200");
						out.println("Server: Java HTTP Server/Shortner : 1.0");
						out.println("Date: " + new Date());
						out.println("Content-type: " + content);
						out.println("Content-length: " + fileLength);
						out.println(); 
						out.flush(); 

						dataOut.write(resultByte, 0, fileLength);
						dataOut.flush();
					} else {
						String content = "text/html";
						out.println("HTTP/1.1 404 File Not Found");
						out.println("Server: Java HTTP Server/Shortner : 1.0");
						out.println("Date: " + new Date());
						out.println("Content-type: " + content);
						out.println("Content-length: " + 0);
						out.println(); 
						out.flush(); 
					}
				} else {
					Pattern pget = Pattern.compile("^(\\S+)\\s+/(\\S+)\\s+(\\S+)$");
					Matcher mget = pget.matcher(input);
					if(mget.matches()){
						String method=mget.group(1);
						String shortResource=mget.group(2);
						String httpVersion=mget.group(3);

						String longResource = entries.get(shortResource);

						if(longResource!=null){
							File file = new File(WEB_ROOT, REDIRECT);
							int fileLength = (int) file.length();
							String contentMimeType = "text/html";
		
							//read content to return to client
							byte[] fileData = readFileData(file, fileLength);
							
							// out.println("HTTP/1.1 301 Moved Permanently");
							out.println("HTTP/1.1 307 Temporary Redirect");
							out.println("Location: "+longResource);
							out.println("Server: Java HTTP Server/Shortner : 1.0");
							out.println("Date: " + new Date());
							out.println("Content-type: " + contentMimeType);
							out.println("Content-length: " + fileLength);
							out.println(); 
							out.flush(); 
		
							dataOut.write(fileData, 0, fileLength);
							dataOut.flush();
						} else {
							// File file = new File(WEB_ROOT, FILE_NOT_FOUND);
							// int fileLength = (int) file.length();
							String content = "text/html";
							// byte[] fileData = readFileData(file, fileLength);
							
							
							out.println("HTTP/1.1 404 File Not Found");
							out.println("Server: Java HTTP Server/Shortner : 1.0");
							out.println("Date: " + new Date());
							out.println("Content-type: " + content);
							out.println("Content-length: " + not_found_file_length);
							out.println(); 
							out.flush(); 
							
							dataOut.write(not_found_file_data, 0, not_found_file_length);
							dataOut.flush();
						}
					} else {
						Pattern pfetch = Pattern.compile("^(\\S+)\\s+/(\\S*)\\s+(\\S+)$");
						Matcher mfetch = pfetch.matcher(input);
						if(mfetch.matches() && mfetch.group(2) == ""){
							File file = new File(WEB_ROOT, DEFAULT_FILE);
							int fileLength = (int) file.length();
							String contentMimeType = "text/html";
							byte[] fileData = readFileData(file, fileLength);
								
							out.println("HTTP/1.1 200 OK");
							out.println("Server: Java HTTP Server/Shortner : 1.0");
							out.println("Date: " + new Date());
							out.println("Content-type: " + contentMimeType);
							out.println("Content-length: " + fileLength);
							out.println(); 
							out.flush(); 

							dataOut.write(fileData, 0, fileLength);
							dataOut.flush();
						} 
					}
				}
			}
		} catch (Exception e) {
			System.err.println("Server error");
		} finally {
			try {
				in.close();
				out.close();
				connect.close(); // we close socket connection
			} catch (Exception e) {
				System.err.println("Error closing stream : " + e.getMessage());
			} 
		}
	}

	private static byte[] readFileData(File file, int fileLength) throws IOException {
		FileInputStream fileIn = null;
		byte[] fileData = new byte[fileLength];
		
		try {
			fileIn = new FileInputStream(file);
			fileIn.read(fileData);
		} finally {
			if (fileIn != null) 
				fileIn.close();
		}
		
		return fileData;
	}

}