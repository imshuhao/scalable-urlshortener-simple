import java.io.*;
import java.net.*;
import java.util.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class SimpleProxyServer {
  static int i = 0;
  // String[] hosts = {"dh2020pc18:8080", "localhost"};
  static List<String> hosts = new ArrayList<>();
  static List<Integer> ports = new ArrayList<>();

  public static void main(String[] args) throws IOException {
    Properties prop = new Properties();
    String configFile = "config.properties";
    try (FileInputStream fis = new FileInputStream(configFile)) {
        prop.load(fis);
    } catch (FileNotFoundException ex) {
      System.exit(1);
    } catch (IOException ex) {
      System.exit(1);
    }

    for (int i = 0; ; ++i) {
        String hostname = prop.getProperty("hostname" + i);
        String port = prop.getProperty("port" + i);
        if (hostname == null || port == null) {
          break;
        }
        hosts.add(hostname);
        ports.add(Integer.parseInt(port));
    }
    System.out.println(hosts);
    try {
      int localport = Integer.parseInt(prop.getProperty("proxyPort"));
      // Print a start-up message
      System.out.println("Starting proxy for " + hosts.size() + " hosts"
          + " on " + ports.size() +  " ports.");
      // And start running the server
      runServer(hosts, ports, localport); // never returns
    } catch (Exception e) {
      System.err.println(e);
    }
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
        // Wait for a connection on the local port
        client = ss.accept();

        final InputStream streamFromClient = client.getInputStream();
        final OutputStream streamToClient = client.getOutputStream();
        // Make a connection to the real server.
        // If we cannot connect to the server, send an error to the
        // client, disconnect, and continue waiting for connections.
        i = (int)(Math.random() * hosts.size());
        String host = hosts.get(i);
        Integer port = ports.get(i++);
        System.out.println("redirecting to" + host + ":" + port);
      

        try {
          server = new Socket(host, port);
        } catch (IOException e) {
          PrintWriter out = new PrintWriter(streamToClient);
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