USE [Recipesdatabse]
GO

/****** Object:  Table [dbo].[Recipes]    Script Date: 21-08-2025 19:31:36 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Recipes](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[cuisine] [nvarchar](255) NULL,
	[title] [nvarchar](255) NOT NULL,
	[rating] [float] NULL,
	[prep_time] [int] NULL,
	[cook_time] [int] NULL,
	[total_time] [int] NULL,
	[description] [nvarchar](max) NULL,
	[nutrients] [nvarchar](max) NULL,
	[serves] [nvarchar](50) NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO


