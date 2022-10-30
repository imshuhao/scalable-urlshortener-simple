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
  static int i = 0;
  // String[] hosts = {"dh2020pc18:8080", "localhost"};
  static List<String> hosts = new ArrayList<>();
  static List<Integer> ports = new ArrayList<>();

  public static void main(String[] args) throws IOException {
    Properties prop = new Properties();
    String configFile = "config.properties";
    // MessageDigest md = MessageDigest.getInstance("MD5");
    
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

  private static Integer hashRequest(String input) {
    String shortResource="arnold";
    Integer hashed = null;
    boolean hb = false;
    try {
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

    byte[] reply = new byte[4096];

    while (true) {
      Socket client = null, server = null;
      try {
        // Wait for a connection on the local port
        client = ss.accept();

        final InputStream streamFromClient = client.getInputStream();
        final OutputStream streamToClient = client.getOutputStream();

        BufferedReader in = new BufferedReader(new InputStreamReader(streamFromClient));
        String clientInput = in.readLine();
        Integer machine2send = hashRequest(clientInput);
        System.out.println(clientInput + machine2send.toString());

        i = 0;
        // i = (int)(Math.random() * hosts.size());
        String host = hosts.get(i);
        Integer port = ports.get(i);
        System.out.println("redirecting to" + host + ":" + port);
      
        try {
          server = new Socket(host, port);
        } catch (IOException e) {
          PrintWriter out = new PrintWriter(streamToClient);
          out.print("Proxy server cannot connect to " + host + ":"+ port + ":\n" + e + "\n");
          out.flush();
          client.close();
          continue;
        }

        Thread t = new Thread(new ThreadWorker(clientInput, server));
        t.start();

        int bytesRead;
        System.out.println("here");
        try {
          while ((bytesRead = server.getInputStream().read(reply)) != -1) {
            client.getOutputStream().write(reply, 0, bytesRead);
            client.getOutputStream().flush();
          }
        } catch (IOException e) {
        }

        // The server closed its connection to us, so we close our
        // connection to our client.
        client.getOutputStream().close();
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


class ThreadWorker implements Runnable {
  private String clientInput;
  private Socket server;
  ThreadWorker(String clientInput, Socket server) {
      this.clientInput = clientInput;
      this.server = server;
  }

  @Override
  public void run() {
    try {
      System.out.println("sending to URLShortner");
      byte[] byteString = this.clientInput.getBytes("UTF-8");
      this.server.getOutputStream().write(byteString, 0, byteString.length);
      this.server.getOutputStream().flush();
      System.out.println("done.");
    } catch (IOException e) {
      System.out.println(e);
    }
    // catch (UnsupportedEncodingException e) {}
  }
}




