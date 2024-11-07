using System;
using System.Drawing;
using System.Net.Sockets;
using System.Text;

class Client
{
    private static async Task SendAllAsync(NetworkStream stream, string data)
    {
        byte[] serializedData = Encoding.UTF8.GetBytes(data);
        byte[] lengthPrefix = BitConverter.GetBytes(serializedData.Length);
        if (BitConverter.IsLittleEndian)
        {
            Array.Reverse(lengthPrefix);
        }
        await stream.WriteAsync(lengthPrefix, 0, lengthPrefix.Length);
        await stream.WriteAsync(serializedData, 0, serializedData.Length);
    }

    private static async Task<string> ReceiveAllAsync(NetworkStream stream)
    {
        byte[] lengthPrefix = new byte[4];
        int bytesRead = await stream.ReadAsync(lengthPrefix, 0, lengthPrefix.Length);
        
        if (BitConverter.IsLittleEndian)
        {
            Array.Reverse(lengthPrefix);
        }
        int dataLength = BitConverter.ToInt32(lengthPrefix, 0);

        byte[] data = new byte[dataLength];
        bytesRead = 0;
        while (bytesRead < dataLength)
        {
            int read = await stream.ReadAsync(data, bytesRead, dataLength - bytesRead);
            bytesRead += read;
        }

        return Encoding.UTF8.GetString(data);
    }

    private static string BitmapToBase64(Bitmap bitmap)
    {
        using (MemoryStream ms = new MemoryStream())
        {
            bitmap.Save(ms, System.Drawing.Imaging.ImageFormat.Png);
            byte[] imageBytes = ms.ToArray();
            return Convert.ToBase64String(imageBytes);
        }
    }

    private static Bitmap Base64ToBitmap(string base64String)
    {
        byte[] imageBytes = Convert.FromBase64String(base64String);
        using (MemoryStream ms = new MemoryStream(imageBytes))
        {
            return new Bitmap(ms);
        }
    }

    private static int[,] ReplicateEdges(int[,] imageArray)
    {
        int height = imageArray.GetLength(0);
        int width = imageArray.GetLength(1);
        int[,] replicatedImage = new int[height + 2, width + 2];

        for (int i = 0; i < height; i++)
            for (int j = 0; j < width; j++)
                replicatedImage[i + 1, j + 1] = imageArray[i, j];

        // Top and bottom edges
        for (int j = 0; j < width; j++)
        {
            replicatedImage[0, j + 1] = imageArray[0, j];
            replicatedImage[height + 1, j + 1] = imageArray[height - 1, j];
        }

        // Left and right edges
        for (int i = 0; i < height; i++)
        {
            replicatedImage[i + 1, 0] = imageArray[i, 0];
            replicatedImage[i + 1, width + 1] = imageArray[i, width - 1];
        }

        // Corners
        replicatedImage[0, 0] = imageArray[0, 0];
        replicatedImage[0, width + 1] = imageArray[0, width - 1];
        replicatedImage[height + 1, 0] = imageArray[height - 1, 0];
        replicatedImage[height + 1, width + 1] = imageArray[height - 1, width - 1];

        return replicatedImage;
    }

    private static Bitmap EdgeFilter(Bitmap image)
    {
        int[,] sobelX = { { -1, 0, 1 }, { -2, 0, 2 }, { -1, 0, 1 } };
        int[,] sobelY = { { 1, 2, 1 }, { 0, 0, 0 }, { -1, -2, -1 } };

        int width = image.Width;
        int height = image.Height;

        int[,] imageArray = new int[height, width];
        for (int i = 0; i < height; i++)
            for (int j = 0; j < width; j++)
            {
                Color pixel = image.GetPixel(j, i);
                int gray = (pixel.R + pixel.G + pixel.B) / 3;
                imageArray[i, j] = gray;
            }

        int[,] replicatedImage = ReplicateEdges(imageArray);
        Bitmap outputImage = new Bitmap(width, height);

        for (int i = 0; i < height; i++)
        {
            for (int j = 0; j < width; j++)
            {
                int gradientX = 0, gradientY = 0;

                for (int x = 0; x < 3; x++)
                    for (int y = 0; y < 3; y++)
                    {
                        int pixel = replicatedImage[i + x, j + y];
                        gradientX += pixel * sobelX[x, y];
                        gradientY += pixel * sobelY[x, y];
                    }

                int gradient = (int)Math.Sqrt(gradientX * gradientX + gradientY * gradientY);
                gradient = Math.Min(255, gradient);
                outputImage.SetPixel(j, i, Color.FromArgb(gradient, gradient, gradient));
            }
        }

        return outputImage;
    }

    public static async Task Main(string[] args)
    {
        string serverIp = "10.104.32.240";
        int port = 2040;

        try
        {
            using (TcpClient client = new TcpClient(serverIp, port))
            using (NetworkStream stream = client.GetStream())
            {
                Console.WriteLine("Połączono z serwerem");

                string base64Fragment = await ReceiveAllAsync(stream);
                Bitmap fragment = Base64ToBitmap(base64Fragment);

                Bitmap processedFragment = EdgeFilter(fragment);

                string base64ProcessedFragment = BitmapToBase64(processedFragment);
                await SendAllAsync(stream, base64ProcessedFragment);

                Console.WriteLine("Fragment przetworzony i wysłany z powrotem do serwera");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}