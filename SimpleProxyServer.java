import java.io.*;
import java.net.*;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class SimpleProxyServer {
  // static int i = 0;
  // String[] hosts = {"dh2020pc18:8080", "localhost"};
  static List<String> hosts = new ArrayList<>();
  static List<Integer> ports = new ArrayList<>();
  static Integer localport=null;

  public static void main(String[] args) throws IOException {
    loadProp();
    try {
      // Print a start-up message
      System.out.println("Starting proxy on port " + localport + " for " + hosts.size() + " hosts"
          + " on " + ports.size() +  " ports.");  
      // And start running the server
      runServer(hosts, ports, localport); // never returns
    } catch (Exception e) {
      System.err.println(e);
    }
  }

  private static void loadProp() {
    Properties prop = new Properties();
    String configFile = "config.properties";
    try (FileInputStream fis = new FileInputStream(configFile)) {
        prop.load(fis);
    } catch (FileNotFoundException ex) {
      System.exit(1);
    } catch (IOException ex) {
      System.exit(1);
    }
    
    localport = Integer.parseInt(prop.getProperty("proxyPort"));

    for (int k = 0; ; ++k) {
        String hostname = prop.getProperty("hostname" + k);
        String port = prop.getProperty("port" + k);
        if (hostname == null || port == null) {
          break;
        }
        hosts.add(hostname);
        ports.add(Integer.parseInt(port));
    }
    System.out.println(hosts);
  }

  private static Integer hashRequest(InputStream streamFromClient) {
    String shortResource="arnold"; Integer hashed = null; boolean hb = false;
    try {
      BufferedReader in = new BufferedReader(new InputStreamReader(streamFromClient));
      String input = in.readLine();

      Pattern pput = Pattern.compile("^PUT\\s+/\\?short=(\\S+)&long=(\\S+)\\s+(\\S+)$");
			Matcher mput = pput.matcher(input);
			if(mput.matches()){
				shortResource=mput.group(1);

      } else {
        Pattern pget = Pattern.compile("^(\\S+)\\s+/(\\S+)\\s+(\\S+)$");
				Matcher mget = pget.matcher(input);
				if(mget.matches()){
					String method=mget.group(1);
					shortResource=mget.group(2);
          if(shortResource.equals("hb")) {
            hb = true;
          }
        }
      }

      MessageDigest md = MessageDigest.getInstance("MD5");
      byte[] dg = md.digest(shortResource.getBytes());
      hashed = Byte.toUnsignedInt(dg[0]);
      hashed = 0;
    } catch (IOException e) {
      System.err.println(e);
    } catch (NoSuchAlgorithmException e) {
      System.err.println(e);
    }
    return hb ? -1 : hashed;
  }

  /**
   * runs a single-threaded proxy server on
   * the specified local port. It never returns.
   */
  public static void runServer(List<String> hosts, List<Integer> ports, int localport)
      throws IOException {
    // Create a ServerSocket to listen for connections with
    ServerSocket ss = new ServerSocket(localport);

    final byte[] request = new byte[1024];
    byte[] reply = new byte[4096];

    while (true) {
      Socket client = null, server = null;
      try {
        client = ss.accept();

        final InputStream streamFromClient = client.getInputStream();
        final OutputStream streamToClient = client.getOutputStream();
        PrintWriter out = new PrintWriter(streamToClient);

        Integer hashed=hashRequest(streamFromClient);
        int i=0;

        if (hashed == -1) {
          out.println("HTTP/1.1 200 OK");
          out.println("Server: Java HTTP Server/Shortner : 1.0");
          out.println("Date: " + new Date());
          out.println(); 
          out.flush();
          client.close();
          continue;
        } else if (hashed != null) {
          i = (int)(hashed % hosts.size());
        } else {
          System.err.println("Unhashed request.");
        }
        String host = hosts.get(i);
        Integer port = ports.get(i);
        System.out.println("redirecting to " + host + ":" + port);

        try {
          server = new Socket(host, port);
        } catch (IOException e) {
          out.print("Proxy server cannot connect to " + host + ":"+ port + ":\n" + 
          e + "\n");
          out.flush();
          client.close();
          continue;
        }

        // Get server streams.
        final InputStream streamFromServer = server.getInputStream();
        final OutputStream streamToServer = server.getOutputStream();

        // a thread to read the client's requests and pass them
        // to the server. A separate thread for asynchronous.
        Thread t = new Thread() {
          public void run() {
            int bytesRead;
            try {
              while ((bytesRead = streamFromClient.read(request)) != -1) {
                streamToServer.write(request, 0, bytesRead);
                streamToServer.flush();
              }
            } catch (IOException e) {
            }

            // the client closed the connection to us, so close our
            // connection to the server.
            try {
              streamToServer.close();
            } catch (IOException e) {
            }
          }
        };

        // Start the client-to-server request thread running
        t.start();

        // Read the server's responses
        // and pass them back to the client.
        int bytesRead;
        try {
          while ((bytesRead = streamFromServer.read(reply)) != -1) {
            streamToClient.write(reply, 0, bytesRead);
            streamToClient.flush();
          }
        } catch (IOException e) {
        }

        // The server closed its connection to us, so we close our
        // connection to our client.
        streamToClient.close();
      } catch (IOException e) {
        System.err.println(e);
      } finally {
        try {
          if (server != null)
            server.close();
          if (client != null)
            client.close();
        } catch (IOException e) {
        }
      }
    }
  }
}